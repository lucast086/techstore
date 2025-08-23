# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cash register validation system for repair deliveries
- System configuration management with database storage
- Configurable default opening balance (currently $10,000)
- Multiple open cash register prevention
- Enhanced error display for HTMX operations
- Comprehensive user guide for cash register management
- Technical documentation for cash validation system

### Fixed
- Repair delivery now requires open cash register
- Error messages properly display in frontend with HTMX
- Cash closing maintains original opening date even when closed on different day

## [0.2.6] - 2025-08-23

### Added
- Credit payment system for customer advances (STORY-073)
- System configuration table for runtime settings
- Cash register validation for repair deliveries
- Configurable default opening balance

### Changed
- Default tax rate changed from 16% to 0% for all products
- Cash opening now uses configurable default instead of last closing balance

### Fixed
- Credit payment precision issue with Decimal type handling
- POS default amount now correctly defaults to 0 instead of full payment
- Cash closing date maintains opening date when closed on different day
- HTTPS scheme forced for static files in production
- Documentation files use relative paths in production

## [0.2.5] - 2025-08-22

### Added
- Spanish translation for remaining English texts in UI
- Product edition feature

### Fixed
- Static file serving in production environment

## [0.2.4] - 2025-08-21

### Added
- Complete Spanish translation of interface

## [0.2.3] - 2025-08-20

### Added
- Initial cash closing functionality
- Basic repair management system

## [0.2.2] - 2025-08-19

### Added
- Customer management module
- Product inventory system

## [0.2.1] - 2025-08-18

### Added
- User authentication and authorization
- Role-based access control (Admin, Manager, Employee)

## [0.2.0] - 2025-08-17

### Added
- Initial FastAPI application structure
- PostgreSQL database integration
- HTMX frontend framework
- Docker development environment

## [0.1.0] - 2025-08-15

### Added
- Initial project setup
- Basic project structure
- Development environment configuration
