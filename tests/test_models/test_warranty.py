"""Tests for warranty models."""

from datetime import date, datetime, timedelta

from app.models.repair import Repair
from app.models.user import User
from app.models.warranty import CoverageType, Warranty, WarrantyClaim, WarrantyStatus
from sqlalchemy.orm import Session


class TestWarrantyModel:
    """Test cases for the Warranty model."""

    def test_create_warranty(
        self,
        db_session: Session,
        test_repair: Repair,
    ) -> None:
        """Test creating a warranty."""
        warranty = Warranty(
            repair_id=test_repair.id,
            warranty_number="WRN-2024-00001",
            coverage_type=CoverageType.FULL,
            parts_warranty_days=90,
            labor_warranty_days=30,
            start_date=date.today(),
            parts_expiry_date=date.today() + timedelta(days=90),
            labor_expiry_date=date.today() + timedelta(days=30),
            status=WarrantyStatus.ACTIVE,
        )

        db_session.add(warranty)
        db_session.commit()
        db_session.refresh(warranty)

        assert warranty.id is not None
        assert warranty.repair_id == test_repair.id
        assert warranty.warranty_number == "WRN-2024-00001"
        assert warranty.coverage_type == CoverageType.FULL
        assert warranty.status == WarrantyStatus.ACTIVE

    def test_warranty_validity_checks(
        self,
        db_session: Session,
        test_repair: Repair,
    ) -> None:
        """Test warranty validity checking methods."""
        # Create warranty with specific dates
        start_date = date.today()
        parts_expiry = start_date + timedelta(days=90)
        labor_expiry = start_date + timedelta(days=30)

        warranty = Warranty(
            repair_id=test_repair.id,
            warranty_number="WRN-2024-00002",
            coverage_type=CoverageType.FULL,
            parts_warranty_days=90,
            labor_warranty_days=30,
            start_date=start_date,
            parts_expiry_date=parts_expiry,
            labor_expiry_date=labor_expiry,
            status=WarrantyStatus.ACTIVE,
        )

        db_session.add(warranty)
        db_session.commit()

        # Test current validity
        assert warranty.is_parts_valid() is True
        assert warranty.is_labor_valid() is True
        assert warranty.is_valid() is True

        # Test with future date (expired)
        future_date = parts_expiry + timedelta(days=1)
        assert warranty.is_parts_valid(future_date) is False
        assert warranty.is_labor_valid(future_date) is False
        assert warranty.is_valid(future_date) is False

        # Test with date when only labor is expired
        mid_date = labor_expiry + timedelta(days=1)
        assert warranty.is_parts_valid(mid_date) is True
        assert warranty.is_labor_valid(mid_date) is False
        assert warranty.is_valid(mid_date) is True  # Still valid due to parts

    def test_warranty_void(
        self,
        db_session: Session,
        test_repair: Repair,
        test_user: User,
    ) -> None:
        """Test voiding a warranty."""
        warranty = Warranty(
            repair_id=test_repair.id,
            warranty_number="WRN-2024-00003",
            coverage_type=CoverageType.FULL,
            parts_warranty_days=90,
            labor_warranty_days=30,
            start_date=date.today(),
            parts_expiry_date=date.today() + timedelta(days=90),
            labor_expiry_date=date.today() + timedelta(days=30),
            status=WarrantyStatus.ACTIVE,
        )

        db_session.add(warranty)
        db_session.commit()

        # Void the warranty
        warranty.status = WarrantyStatus.VOIDED
        warranty.void_reason = "Customer damaged device"
        warranty.voided_at = datetime.utcnow()
        warranty.voided_by = test_user.id

        db_session.commit()
        db_session.refresh(warranty)

        assert warranty.status == WarrantyStatus.VOIDED
        assert warranty.void_reason == "Customer damaged device"
        assert warranty.voided_at is not None
        assert warranty.voided_by == test_user.id

        # Voided warranty should not be valid
        assert warranty.is_valid() is False

    def test_warranty_repair_relationship(
        self,
        db_session: Session,
        test_repair: Repair,
    ) -> None:
        """Test warranty-repair relationship."""
        warranty = Warranty(
            repair_id=test_repair.id,
            warranty_number="WRN-2024-00004",
            coverage_type=CoverageType.FULL,
            parts_warranty_days=90,
            labor_warranty_days=30,
            start_date=date.today(),
            parts_expiry_date=date.today() + timedelta(days=90),
            labor_expiry_date=date.today() + timedelta(days=30),
            status=WarrantyStatus.ACTIVE,
        )

        db_session.add(warranty)
        db_session.commit()
        db_session.refresh(warranty)

        # Test relationship
        assert warranty.repair is not None
        assert warranty.repair.id == test_repair.id
        assert test_repair.warranty is not None
        assert test_repair.warranty.id == warranty.id


class TestWarrantyClaimModel:
    """Test cases for the WarrantyClaim model."""

    def test_create_warranty_claim(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_repair: Repair,
        test_user: User,
    ) -> None:
        """Test creating a warranty claim."""
        claim = WarrantyClaim(
            warranty_id=test_warranty.id,
            repair_id=test_repair.id,
            claim_number="CLM-2024-00001",
            claim_date=date.today(),
            issue_description="Device not charging",
            parts_covered=True,
            labor_covered=True,
            approved=True,
            approved_by=test_user.id,
            approved_at=datetime.utcnow(),
        )

        db_session.add(claim)
        db_session.commit()
        db_session.refresh(claim)

        assert claim.id is not None
        assert claim.warranty_id == test_warranty.id
        assert claim.repair_id == test_repair.id
        assert claim.claim_number == "CLM-2024-00001"
        assert claim.issue_description == "Device not charging"
        assert claim.parts_covered is True
        assert claim.labor_covered is True
        assert claim.approved is True

    def test_claim_warranty_relationship(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_repair: Repair,
    ) -> None:
        """Test warranty claim relationships."""
        claim = WarrantyClaim(
            warranty_id=test_warranty.id,
            repair_id=test_repair.id,
            claim_number="CLM-2024-00002",
            claim_date=date.today(),
            issue_description="Screen flickering",
            parts_covered=False,
            labor_covered=True,
        )

        db_session.add(claim)
        db_session.commit()
        db_session.refresh(claim)

        # Test relationships
        assert claim.warranty is not None
        assert claim.warranty.id == test_warranty.id
        assert claim.repair is not None
        assert claim.repair.id == test_repair.id

        # Test reverse relationship
        assert len(test_warranty.claims) == 1
        assert test_warranty.claims[0].id == claim.id

    def test_claim_approval_tracking(
        self,
        db_session: Session,
        test_warranty: Warranty,
        test_repair: Repair,
        test_user: User,
    ) -> None:
        """Test warranty claim approval tracking."""
        claim = WarrantyClaim(
            warranty_id=test_warranty.id,
            repair_id=test_repair.id,
            claim_number="CLM-2024-00003",
            claim_date=date.today(),
            issue_description="Battery issue",
            parts_covered=True,
            labor_covered=False,
            approved=False,  # Start as not approved
        )

        db_session.add(claim)
        db_session.commit()

        # Approve the claim
        claim.approved = True
        claim.approved_by = test_user.id
        claim.approved_at = datetime.utcnow()
        claim.resolution_notes = "Approved for battery replacement"

        db_session.commit()
        db_session.refresh(claim)

        assert claim.approved is True
        assert claim.approved_by == test_user.id
        assert claim.approved_at is not None
        assert claim.resolution_notes == "Approved for battery replacement"
