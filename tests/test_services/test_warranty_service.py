"""Tests for warranty service."""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from app.models.repair import Repair
from app.models.warranty import Warranty, WarrantyStatus
from app.schemas.repair import RepairStatus
from app.schemas.warranty import (
    WarrantyCheckRequest,
    WarrantyClaimCreate,
    WarrantyCreate,
    WarrantySearchParams,
    WarrantyVoid,
)
from app.services.warranty_service import warranty_service
from sqlalchemy.orm import Session


class TestWarrantyService:
    """Test cases for warranty service."""

    def test_create_warranty_for_repair(
        self,
        db_session: Session,
        test_repair: Repair,
    ) -> None:
        """Test creating warranty for a delivered repair."""
        # Set repair status to delivered
        test_repair.status = RepairStatus.DELIVERED.value
        db_session.commit()

        # Create warranty
        warranty_data = WarrantyCreate(
            repair_id=test_repair.id,
            parts_warranty_days=90,
            labor_warranty_days=30,
        )

        result = warranty_service.create_warranty_for_repair(
            db_session,
            repair_id=test_repair.id,
            warranty_data=warranty_data,
        )

        assert result.repair_id == test_repair.id
        assert result.parts_warranty_days == 90
        assert result.labor_warranty_days == 30
        assert result.status == WarrantyStatus.ACTIVE
        assert result.warranty_number.startswith("WRN-")

    def test_create_warranty_for_non_delivered_repair(
        self,
        db_session: Session,
        test_repair: Repair,
    ) -> None:
        """Test creating warranty for non-delivered repair should fail."""
        # Keep repair in non-delivered status
        test_repair.status = RepairStatus.RECEIVED.value
        db_session.commit()

        warranty_data = WarrantyCreate(repair_id=test_repair.id)

        with pytest.raises(ValueError, match="delivered"):
            warranty_service.create_warranty_for_repair(
                db_session,
                repair_id=test_repair.id,
                warranty_data=warranty_data,
            )

    def test_create_duplicate_warranty(
        self,
        db_session: Session,
        test_repair: Repair,
        test_warranty: Warranty,
    ) -> None:
        """Test creating duplicate warranty should fail."""
        # Repair already has warranty
        test_repair.status = RepairStatus.DELIVERED.value
        db_session.commit()

        warranty_data = WarrantyCreate(repair_id=test_repair.id)

        with pytest.raises(ValueError, match="already exists"):
            warranty_service.create_warranty_for_repair(
                db_session,
                repair_id=test_repair.id,
                warranty_data=warranty_data,
            )

    def test_void_warranty(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_user,
    ) -> None:
        """Test voiding a warranty."""
        void_data = WarrantyVoid(
            void_reason="Customer damaged device",
            voided_by=test_user.id,
        )

        result = warranty_service.void_warranty(
            db_session,
            warranty_id=test_warranty.id,
            void_data=void_data,
        )

        assert result.status == WarrantyStatus.VOIDED
        assert result.void_reason == "Customer damaged device"
        assert result.voided_by == test_user.id
        assert result.voided_at is not None

    def test_check_warranty_by_warranty_number(
        self,
        db_session: Session,
        test_warranty: Warranty,
    ) -> None:
        """Test checking warranty by warranty number."""
        request = WarrantyCheckRequest(
            warranty_number=test_warranty.warranty_number,
        )

        result = warranty_service.check_warranty(db_session, request=request)

        assert result.found is True
        assert len(result.warranties) == 1
        assert result.warranties[0].warranty_number == test_warranty.warranty_number

    def test_check_warranty_not_found(
        self,
        db_session: Session,
    ) -> None:
        """Test checking warranty that doesn't exist."""
        request = WarrantyCheckRequest(
            warranty_number="WRN-9999-99999",
        )

        result = warranty_service.check_warranty(db_session, request=request)

        assert result.found is False
        assert len(result.warranties) == 0
        assert "No warranty found" in result.message

    def test_search_warranties(
        self,
        db_session: Session,
        test_warranty: Warranty,
    ) -> None:
        """Test searching warranties."""
        params = WarrantySearchParams(
            q=test_warranty.warranty_number,
            page=1,
            page_size=20,
        )

        warranties, total = warranty_service.search_warranties(
            db_session,
            params=params,
        )

        assert total == 1
        assert len(warranties) == 1
        assert warranties[0].warranty_number == test_warranty.warranty_number

    def test_create_warranty_claim(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_user,
    ) -> None:
        """Test creating a warranty claim."""
        claim_data = WarrantyClaimCreate(
            warranty_id=test_warranty.id,
            issue_description="Device not charging",
            parts_covered=True,
            labor_covered=True,
        )

        # Mock the repair creation
        with patch.object(warranty_service, "_build_claim_response") as mock_build:
            mock_response = Mock()
            mock_response.claim_number = "CLM-2024-00001"
            mock_build.return_value = mock_response

            result = warranty_service.create_warranty_claim(
                db_session,
                claim_data=claim_data,
                current_user_id=test_user.id,
            )

            assert result.claim_number == "CLM-2024-00001"

    def test_create_claim_for_expired_warranty(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_user,
    ) -> None:
        """Test creating claim for expired warranty should fail."""
        # Set warranty as expired
        test_warranty.parts_expiry_date = date.today() - timedelta(days=1)
        test_warranty.labor_expiry_date = date.today() - timedelta(days=1)
        db_session.commit()

        claim_data = WarrantyClaimCreate(
            warranty_id=test_warranty.id,
            issue_description="Device issue",
            parts_covered=True,
            labor_covered=True,
        )

        with pytest.raises(ValueError, match="expired"):
            warranty_service.create_warranty_claim(
                db_session,
                claim_data=claim_data,
                current_user_id=test_user.id,
            )

    def test_get_warranty_statistics(
        self,
        db_session: Session,
        test_warranty: Warranty,
    ) -> None:
        """Test getting warranty statistics."""
        stats = warranty_service.get_warranty_statistics(db_session)

        assert stats.total_warranties >= 1
        assert stats.active_warranties >= 1
        assert stats.expired_warranties >= 0
        assert stats.claim_rate >= 0.0

    def test_update_expired_warranties(
        self,
        db_session: Session,
        test_warranty: Warranty,
    ) -> None:
        """Test updating expired warranties."""
        # Create an expired warranty
        test_warranty.parts_expiry_date = date.today() - timedelta(days=1)
        test_warranty.labor_expiry_date = date.today() - timedelta(days=1)
        db_session.commit()

        count = warranty_service.update_expired_warranties(db_session)

        assert count >= 1

        # Refresh and check status
        db_session.refresh(test_warranty)
        assert test_warranty.status == WarrantyStatus.EXPIRED
