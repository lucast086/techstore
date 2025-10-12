"""CRUD operations for warranty management."""

from datetime import timedelta
from typing import Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.repair import Repair
from app.models.warranty import Warranty, WarrantyClaim, WarrantyStatus
from app.schemas.warranty import (
    WarrantyClaimCreate,
    WarrantyClaimUpdate,
    WarrantyCreate,
    WarrantySearchParams,
    WarrantyUpdate,
    WarrantyVoid,
)
from app.utils.timezone import get_local_today, get_utc_now


class CRUDWarranty(CRUDBase[Warranty, WarrantyCreate, WarrantyUpdate]):
    """CRUD operations for warranties."""

    def create_warranty(
        self,
        db: Session,
        *,
        repair_id: int,
        warranty_create: WarrantyCreate,
    ) -> Warranty:
        """Create warranty for a delivered repair."""
        # Generate warranty number
        warranty_number = self._generate_warranty_number(db)

        # Calculate expiry dates
        start_date = get_local_today()
        parts_expiry_date = start_date + timedelta(
            days=warranty_create.parts_warranty_days
        )
        labor_expiry_date = start_date + timedelta(
            days=warranty_create.labor_warranty_days
        )

        # Create warranty
        db_warranty = Warranty(
            repair_id=repair_id,
            warranty_number=warranty_number,
            coverage_type=warranty_create.coverage_type,
            parts_warranty_days=warranty_create.parts_warranty_days,
            labor_warranty_days=warranty_create.labor_warranty_days,
            start_date=start_date,
            parts_expiry_date=parts_expiry_date,
            labor_expiry_date=labor_expiry_date,
            terms=warranty_create.terms,
            exclusions=warranty_create.exclusions,
            status=WarrantyStatus.ACTIVE,
        )

        db.add(db_warranty)
        db.commit()
        db.refresh(db_warranty)

        return db_warranty

    def void_warranty(
        self,
        db: Session,
        *,
        warranty_id: int,
        void_data: WarrantyVoid,
    ) -> Optional[Warranty]:
        """Void a warranty."""
        warranty = self.get(db, id=warranty_id)
        if not warranty:
            return None

        warranty.status = WarrantyStatus.VOIDED
        warranty.void_reason = void_data.void_reason
        warranty.voided_at = get_utc_now()
        warranty.voided_by = void_data.voided_by

        db.commit()
        db.refresh(warranty)

        return warranty

    def get_by_warranty_number(
        self,
        db: Session,
        *,
        warranty_number: str,
    ) -> Optional[Warranty]:
        """Get warranty by warranty number."""
        return (
            db.query(Warranty)
            .filter(Warranty.warranty_number == warranty_number)
            .first()
        )

    def get_by_repair_id(
        self,
        db: Session,
        *,
        repair_id: int,
    ) -> Optional[Warranty]:
        """Get warranty by repair ID."""
        return db.query(Warranty).filter(Warranty.repair_id == repair_id).first()

    def search_warranties(
        self,
        db: Session,
        *,
        params: WarrantySearchParams,
    ) -> tuple[list[Warranty], int]:
        """Search warranties with filters."""
        query = (
            db.query(Warranty)
            .join(Repair, Warranty.repair_id == Repair.id)
            .options(joinedload(Warranty.repair).joinedload(Repair.customer))
        )

        # Search filter
        if params.q:
            search_term = f"%{params.q}%"
            query = query.filter(
                or_(
                    Warranty.warranty_number.ilike(search_term),
                    Repair.repair_number.ilike(search_term),
                )
            )

        # Status filter
        if params.status:
            query = query.filter(Warranty.status == params.status)

        # Customer filter
        if params.customer_id:
            query = query.filter(Repair.customer_id == params.customer_id)

        # Expired filter
        if params.expired is not None:
            today = get_local_today()
            if params.expired:
                query = query.filter(
                    and_(
                        Warranty.parts_expiry_date < today,
                        Warranty.labor_expiry_date < today,
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Warranty.parts_expiry_date >= today,
                        Warranty.labor_expiry_date >= today,
                    )
                )

        # Get total count
        total = query.count()

        # Apply pagination
        warranties = query.offset(params.offset).limit(params.page_size).all()

        return warranties, total

    def check_warranty(
        self,
        db: Session,
        *,
        warranty_number: Optional[str] = None,
        repair_number: Optional[str] = None,
        customer_phone: Optional[str] = None,
    ) -> list[Warranty]:
        """Check warranty validity by various criteria."""
        query = (
            db.query(Warranty)
            .join(Repair, Warranty.repair_id == Repair.id)
            .options(joinedload(Warranty.repair).joinedload(Repair.customer))
        )

        if warranty_number:
            query = query.filter(Warranty.warranty_number == warranty_number)
        elif repair_number:
            query = query.filter(Repair.repair_number == repair_number)
        elif customer_phone:
            query = query.join(Repair.customer).filter(
                func.replace(Repair.customer.property.mapper.class_.phone, " ", "")
                == customer_phone.replace(" ", "")
            )

        return query.all()

    def update_expired_warranties(self, db: Session) -> int:
        """Update status of expired warranties."""
        today = get_local_today()

        expired_warranties = (
            db.query(Warranty)
            .filter(
                and_(
                    Warranty.status == WarrantyStatus.ACTIVE,
                    Warranty.parts_expiry_date < today,
                    Warranty.labor_expiry_date < today,
                )
            )
            .all()
        )

        for warranty in expired_warranties:
            warranty.status = WarrantyStatus.EXPIRED

        db.commit()

        return len(expired_warranties)

    def get_statistics(self, db: Session) -> dict:
        """Get warranty statistics."""
        total_warranties = db.query(func.count(Warranty.id)).scalar() or 0

        active_warranties = (
            db.query(func.count(Warranty.id))
            .filter(Warranty.status == WarrantyStatus.ACTIVE)
            .scalar()
            or 0
        )

        expired_warranties = (
            db.query(func.count(Warranty.id))
            .filter(Warranty.status == WarrantyStatus.EXPIRED)
            .scalar()
            or 0
        )

        claimed_warranties = (
            db.query(func.count(Warranty.id))
            .filter(Warranty.status == WarrantyStatus.CLAIMED)
            .scalar()
            or 0
        )

        voided_warranties = (
            db.query(func.count(Warranty.id))
            .filter(Warranty.status == WarrantyStatus.VOIDED)
            .scalar()
            or 0
        )

        total_claims = db.query(func.count(WarrantyClaim.id)).scalar() or 0

        approved_claims = (
            db.query(func.count(WarrantyClaim.id))
            .filter(WarrantyClaim.approved.is_(True))
            .scalar()
            or 0
        )

        # Calculate claim rate
        claim_rate = 0.0
        if total_warranties > 0:
            claim_rate = (claimed_warranties / total_warranties) * 100

        # Calculate average claim days
        avg_claim_days_result = (
            db.query(
                func.avg(
                    func.julianday(WarrantyClaim.claim_date)
                    - func.julianday(Warranty.start_date)
                )
            )
            .join(Warranty, WarrantyClaim.warranty_id == Warranty.id)
            .scalar()
        )

        avg_claim_days = float(avg_claim_days_result) if avg_claim_days_result else None

        return {
            "total_warranties": total_warranties,
            "active_warranties": active_warranties,
            "expired_warranties": expired_warranties,
            "claimed_warranties": claimed_warranties,
            "voided_warranties": voided_warranties,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "claim_rate": round(claim_rate, 2),
            "average_claim_days": round(avg_claim_days, 1) if avg_claim_days else None,
        }

    def _generate_warranty_number(self, db: Session) -> str:
        """Generate unique warranty number."""
        year = get_utc_now().year

        # Get the last warranty number for the current year
        last_warranty = (
            db.query(Warranty)
            .filter(Warranty.warranty_number.like(f"WRN-{year}-%"))
            .order_by(Warranty.id.desc())
            .first()
        )

        if last_warranty:
            last_number = int(last_warranty.warranty_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"WRN-{year}-{new_number:05d}"


class CRUDWarrantyClaim(
    CRUDBase[WarrantyClaim, WarrantyClaimCreate, WarrantyClaimUpdate]
):
    """CRUD operations for warranty claims."""

    def create_claim(
        self,
        db: Session,
        *,
        claim_create: WarrantyClaimCreate,
        repair_id: int,
    ) -> WarrantyClaim:
        """Create a warranty claim."""
        # Generate claim number
        claim_number = self._generate_claim_number(db)

        # Create claim
        db_claim = WarrantyClaim(
            warranty_id=claim_create.warranty_id,
            repair_id=repair_id,
            claim_number=claim_number,
            claim_date=get_local_today(),
            issue_description=claim_create.issue_description,
            parts_covered=claim_create.parts_covered,
            labor_covered=claim_create.labor_covered,
            approved=True,
            approved_by=claim_create.approved_by,
            approved_at=get_utc_now() if claim_create.approved_by else None,
        )

        db.add(db_claim)

        # Update warranty status
        warranty = (
            db.query(Warranty).filter(Warranty.id == claim_create.warranty_id).first()
        )
        if warranty:
            warranty.status = WarrantyStatus.CLAIMED

        db.commit()
        db.refresh(db_claim)

        return db_claim

    def update_claim(
        self,
        db: Session,
        *,
        claim_id: int,
        claim_update: WarrantyClaimUpdate,
    ) -> Optional[WarrantyClaim]:
        """Update a warranty claim."""
        claim = self.get(db, id=claim_id)
        if not claim:
            return None

        if claim_update.resolution_notes is not None:
            claim.resolution_notes = claim_update.resolution_notes

        if claim_update.approved is not None:
            claim.approved = claim_update.approved
            claim.approved_by = claim_update.approved_by
            claim.approved_at = get_utc_now() if claim_update.approved_by else None

        db.commit()
        db.refresh(claim)

        return claim

    def get_claims_by_warranty(
        self,
        db: Session,
        *,
        warranty_id: int,
    ) -> list[WarrantyClaim]:
        """Get all claims for a warranty."""
        return (
            db.query(WarrantyClaim)
            .filter(WarrantyClaim.warranty_id == warranty_id)
            .all()
        )

    def _generate_claim_number(self, db: Session) -> str:
        """Generate unique claim number."""
        year = get_utc_now().year

        # Get the last claim number for the current year
        last_claim = (
            db.query(WarrantyClaim)
            .filter(WarrantyClaim.claim_number.like(f"CLM-{year}-%"))
            .order_by(WarrantyClaim.id.desc())
            .first()
        )

        if last_claim:
            last_number = int(last_claim.claim_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"CLM-{year}-{new_number:05d}"


# Create instances
warranty = CRUDWarranty(Warranty)
warranty_claim = CRUDWarrantyClaim(WarrantyClaim)
