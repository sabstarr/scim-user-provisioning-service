"""
Bulk import service for SCIM 2.0 endpoints.
Handles CSV file parsing and bulk user creation with comprehensive error handling.
"""

import csv
import io
import time
from typing import List, Dict, Any, Tuple, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import logging

from .schemas import (
    CSVUserRow, SCIMUserCreate, EmailSchema, BulkImportResponse, 
    BulkUserResult, BulkImportStatus, BulkImportRequest
)
from .database_service import DatabaseService

logger = logging.getLogger(__name__)


class BulkImportService:
    """Service for handling bulk user imports from CSV files."""
    
    # Expected CSV column headers
    REQUIRED_COLUMNS = ['userName', 'firstName', 'surName', 'email']
    OPTIONAL_COLUMNS = ['displayName', 'secondaryEmail', 'externalId', 'active']
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # Maximum number of users per import
    MAX_USERS_PER_IMPORT = 1000

    @staticmethod
    def validate_csv_file(file: UploadFile) -> Tuple[bool, List[str]]:
        """
        Validate the uploaded CSV file.
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check file type
        if not file.filename.lower().endswith('.csv'):
            errors.append("File must be a CSV file with .csv extension")
        
        # Check file size
        if file.size and file.size > BulkImportService.MAX_FILE_SIZE:
            errors.append(f"File size {file.size} bytes exceeds maximum allowed size of {BulkImportService.MAX_FILE_SIZE} bytes")
        
        return len(errors) == 0, errors

    @staticmethod
    async def parse_csv_content(file: UploadFile) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse CSV file content and validate structure.
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            Tuple of (parsed_rows, validation_errors)
        """
        errors = []
        rows = []
        
        try:
            # Read file content
            content = await file.read()
            content_str = content.decode('utf-8-sig')  # Handle BOM
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(content_str))
            
            # Validate headers
            if not csv_reader.fieldnames:
                errors.append("CSV file appears to be empty or malformed")
                return rows, errors
            
            headers = [h.strip() for h in csv_reader.fieldnames if h]
            
            # Check required columns
            missing_required = set(BulkImportService.REQUIRED_COLUMNS) - set(headers)
            if missing_required:
                errors.append(f"Missing required columns: {', '.join(missing_required)}")
                return rows, errors
            
            # Check for unexpected columns
            unexpected_columns = set(headers) - set(BulkImportService.ALL_COLUMNS)
            if unexpected_columns:
                logger.warning(f"Unexpected columns found (will be ignored): {', '.join(unexpected_columns)}")
            
            # Parse rows
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
                if len(rows) >= BulkImportService.MAX_USERS_PER_IMPORT:
                    errors.append(f"Maximum number of users ({BulkImportService.MAX_USERS_PER_IMPORT}) exceeded")
                    break
                
                # Clean and filter row data
                cleaned_row = {}
                for col in BulkImportService.ALL_COLUMNS:
                    if col in row and row[col] is not None:
                        value = str(row[col]).strip()
                        if value:  # Only include non-empty values
                            # Convert boolean values
                            if col == 'active':
                                if value.lower() in ['true', '1', 'yes', 'active']:
                                    cleaned_row[col] = True
                                elif value.lower() in ['false', '0', 'no', 'inactive']:
                                    cleaned_row[col] = False
                                else:
                                    cleaned_row[col] = True  # Default to active
                            else:
                                cleaned_row[col] = value
                
                # Add row number for tracking
                cleaned_row['_row_number'] = row_num
                
                # Skip completely empty rows
                if len(cleaned_row) > 1:  # More than just row number
                    rows.append(cleaned_row)
            
            if not rows:
                errors.append("No valid user data found in CSV file")
            
        except UnicodeDecodeError:
            errors.append("Unable to decode CSV file. Please ensure it's saved as UTF-8")
        except csv.Error as e:
            errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing CSV: {str(e)}")
            errors.append(f"Unexpected error parsing CSV file: {str(e)}")
        
        return rows, errors

    @staticmethod
    def validate_user_row(row_data: Dict[str, Any], row_number: int) -> Tuple[Optional[CSVUserRow], List[str]]:
        """
        Validate a single user row against the schema.
        
        Args:
            row_data: Dictionary containing user data from CSV
            row_number: Row number for error reporting
            
        Returns:
            Tuple of (validated_user_or_none, validation_errors)
        """
        errors = []
        
        try:
            # Remove internal fields
            clean_data = {k: v for k, v in row_data.items() if not k.startswith('_')}
            
            # Validate using Pydantic model
            validated_user = CSVUserRow(**clean_data)
            return validated_user, errors
            
        except Exception as e:
            if hasattr(e, 'errors'):
                # Pydantic validation errors
                for error in e.errors():
                    field = error.get('loc', ['unknown'])[0]
                    message = error.get('msg', 'Validation error')
                    errors.append(f"Row {row_number}: {field} - {message}")
            else:
                errors.append(f"Row {row_number}: {str(e)}")
            
            return None, errors

    @staticmethod
    def csv_user_to_scim_user(csv_user: CSVUserRow) -> SCIMUserCreate:
        """
        Convert validated CSV user to SCIM user creation schema.
        
        Args:
            csv_user: Validated CSV user data
            
        Returns:
            SCIM user creation schema
        """
        # Build emails list
        emails = [EmailSchema(value=csv_user.email, primary=True)]
        if csv_user.secondaryEmail:
            emails.append(EmailSchema(value=csv_user.secondaryEmail, primary=False))
        
        return SCIMUserCreate(
            userName=csv_user.userName,
            firstName=csv_user.firstName,
            surName=csv_user.surName,
            displayName=csv_user.displayName,
            emails=emails,
            externalId=csv_user.externalId,
            active=csv_user.active
        )

    @staticmethod
    async def process_bulk_import(
        file: UploadFile,
        realm_id: str,
        db: Session,
        admin_username: str,
        params: BulkImportRequest
    ) -> BulkImportResponse:
        """
        Process bulk user import from CSV file.
        
        Args:
            file: Uploaded CSV file
            realm_id: Target realm ID
            db: Database session
            admin_username: Admin performing the import
            params: Import parameters
            
        Returns:
            Detailed import results
        """
        start_time = time.time()
        
        logger.info(f"Starting bulk import for realm {realm_id} by admin {admin_username}")
        logger.info(f"Import parameters: dry_run={params.dry_run}, skip_duplicates={params.skip_duplicates}, continue_on_error={params.continue_on_error}")
        
        # Initialize results
        results = []
        csv_errors = []
        general_errors = []
        successful_count = 0
        failed_count = 0
        skipped_count = 0
        
        try:
            # Validate file
            file_valid, file_errors = BulkImportService.validate_csv_file(file)
            if not file_valid:
                return BulkImportResponse(
                    status=BulkImportStatus.FAILED,
                    total_rows=0,
                    successful_imports=0,
                    failed_imports=0,
                    skipped_imports=0,
                    processing_time_seconds=time.time() - start_time,
                    results=[],
                    errors=file_errors,
                    csv_validation_errors=file_errors
                )
            
            # Parse CSV content
            rows, parse_errors = await BulkImportService.parse_csv_content(file)
            csv_errors.extend(parse_errors)
            
            if parse_errors and not rows:
                return BulkImportResponse(
                    status=BulkImportStatus.FAILED,
                    total_rows=0,
                    successful_imports=0,
                    failed_imports=0,
                    skipped_imports=0,
                    processing_time_seconds=time.time() - start_time,
                    results=[],
                    errors=parse_errors,
                    csv_validation_errors=parse_errors
                )
            
            # Process each row
            for row_data in rows:
                row_number = row_data.get('_row_number', 0)
                
                # Validate row
                validated_user, validation_errors = BulkImportService.validate_user_row(row_data, row_number)
                
                if validation_errors:
                    failed_count += 1
                    results.append(BulkUserResult(
                        row_number=row_number,
                        userName=row_data.get('userName', 'Unknown'),
                        status="error",
                        message="Validation failed",
                        errors=validation_errors
                    ))
                    
                    if not params.continue_on_error:
                        break
                    continue
                
                if not validated_user:
                    failed_count += 1
                    results.append(BulkUserResult(
                        row_number=row_number,
                        userName=row_data.get('userName', 'Unknown'),
                        status="error",
                        message="Unable to validate user data"
                    ))
                    continue
                
                # Check for duplicates
                if params.skip_duplicates:
                    existing_user = DatabaseService.get_scim_user_by_username(db, validated_user.userName, realm_id)
                    if existing_user:
                        skipped_count += 1
                        results.append(BulkUserResult(
                            row_number=row_number,
                            userName=validated_user.userName,
                            status="skipped",
                            message=f"User '{validated_user.userName}' already exists in realm"
                        ))
                        continue
                
                # Process user creation
                if params.dry_run:
                    # Dry run - just validate
                    successful_count += 1
                    results.append(BulkUserResult(
                        row_number=row_number,
                        userName=validated_user.userName,
                        status="success",
                        message="Validation successful (dry run)"
                    ))
                else:
                    # Actually create the user
                    try:
                        scim_user = BulkImportService.csv_user_to_scim_user(validated_user)
                        created_user = DatabaseService.create_scim_user(db, scim_user, realm_id)
                        
                        successful_count += 1
                        results.append(BulkUserResult(
                            row_number=row_number,
                            userName=validated_user.userName,
                            status="success",
                            user_id=created_user.user_id,
                            message=f"User '{validated_user.userName}' created successfully"
                        ))
                        
                        logger.info(f"Created user {validated_user.userName} with ID {created_user.user_id}")
                        
                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Failed to create user: {str(e)}"
                        
                        results.append(BulkUserResult(
                            row_number=row_number,
                            userName=validated_user.userName,
                            status="error",
                            message=error_msg
                        ))
                        
                        logger.error(f"Error creating user {validated_user.userName}: {str(e)}")
                        
                        if not params.continue_on_error:
                            break
            
            # Determine overall status
            total_rows = len(rows)
            if failed_count == 0 and len(csv_errors) == 0:
                status = BulkImportStatus.SUCCESS
            elif successful_count > 0:
                status = BulkImportStatus.PARTIAL_SUCCESS
            else:
                status = BulkImportStatus.FAILED
            
            processing_time = time.time() - start_time
            
            logger.info(f"Bulk import completed: {successful_count} successful, {failed_count} failed, {skipped_count} skipped in {processing_time:.2f}s")
            
            return BulkImportResponse(
                status=status,
                total_rows=total_rows,
                successful_imports=successful_count,
                failed_imports=failed_count,
                skipped_imports=skipped_count,
                processing_time_seconds=processing_time,
                results=results,
                errors=general_errors if general_errors else None,
                csv_validation_errors=csv_errors if csv_errors else None
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during bulk import: {str(e)}")
            
            return BulkImportResponse(
                status=BulkImportStatus.FAILED,
                total_rows=0,
                successful_imports=0,
                failed_imports=0,
                skipped_imports=0,
                processing_time_seconds=time.time() - start_time,
                results=results,
                errors=[f"Unexpected error: {str(e)}"]
            )

    @staticmethod
    def generate_csv_template() -> str:
        """
        Generate a CSV template with example data.
        
        Returns:
            CSV template as string
        """
        template_data = [
            {
                'userName': 'jdoe',
                'firstName': 'John',
                'surName': 'Doe',
                'displayName': 'John Doe',
                'email': 'john.doe@company.com',
                'secondaryEmail': 'john.doe.alt@company.com',
                'externalId': 'EMP001',
                'active': 'true'
            },
            {
                'userName': 'asmith',
                'firstName': 'Alice',
                'surName': 'Smith',
                'displayName': 'Alice Smith',
                'email': 'alice.smith@company.com',
                'secondaryEmail': '',
                'externalId': 'EMP002',
                'active': 'true'
            },
            {
                'userName': 'bjohnson',
                'firstName': 'Bob',
                'surName': 'Johnson',
                'displayName': '',  # Will be auto-generated
                'email': 'bob.johnson@company.com',
                'secondaryEmail': '',
                'externalId': '',
                'active': 'false'
            }
        ]
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=BulkImportService.ALL_COLUMNS)
        writer.writeheader()
        writer.writerows(template_data)
        
        return output.getvalue()
