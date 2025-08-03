import sqlite3
from datetime import datetime
import json
from typing import Dict, Any, Optional, List
import os

class JobDatabase:
    """SQLite database for storing Webhound job data"""
    
    def __init__(self, db_path='webhound.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute('PRAGMA foreign_keys = ON')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    dataset TEXT,
                    sources TEXT,
                    raw_data TEXT,
                    total_records INTEGER DEFAULT 0,
                    validation_status TEXT,
                    quality_score TEXT,
                    validation_notes TEXT,
                    user_rating TEXT DEFAULT NULL,
                    rating_timestamp TIMESTAMP,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Add columns if they don't exist (migrations) - DO THIS FIRST
            columns_to_add = [
                ('raw_data', 'TEXT'),
                ('user_rating', 'TEXT DEFAULT NULL'),
                ('rating_timestamp', 'TIMESTAMP')
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    conn.execute(f'ALTER TABLE jobs ADD COLUMN {column_name} {column_type}')
                    print(f"Added {column_name} column to existing database")
                except sqlite3.OperationalError:
                    # Column already exists, ignore
                    pass
            
            # Create index for faster queries - DO THIS AFTER COLUMNS EXIST
            conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_user_rating ON jobs(user_rating)')
            
            # Commit the changes
            conn.commit()
    
    def create_job(self, job_id: str, query: str) -> None:
        """Create a new job record"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO jobs (job_id, query, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (job_id, query, 'processing', datetime.now(), datetime.now()))
            conn.commit()
    
    def update_job(self, job_id: str, **kwargs) -> None:
        """Update job fields"""
        with sqlite3.connect(self.db_path) as conn:
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['dataset', 'sources', 'raw_data'] and isinstance(value, (list, dict)):
                    # Serialize lists/dicts to JSON for storage
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.append(datetime.now())  # updated_at
            values.append(job_id)
            
            conn.execute(f'''
                UPDATE jobs 
                SET {', '.join(updates)}, updated_at = ?
                WHERE job_id = ?
            ''', values)
            conn.commit()
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
            row = cursor.fetchone()
            
            if row:
                # Convert row to dict
                columns = [description[0] for description in cursor.description]
                job_dict = dict(zip(columns, row))
                
                # Deserialize JSON fields
                if job_dict.get('dataset'):
                    try:
                        job_dict['dataset'] = json.loads(job_dict['dataset'])
                    except json.JSONDecodeError:
                        job_dict['dataset'] = []
                
                if job_dict.get('sources'):
                    try:
                        job_dict['sources'] = json.loads(job_dict['sources'])
                    except json.JSONDecodeError:
                        job_dict['sources'] = []
                
                if job_dict.get('raw_data'):
                    try:
                        job_dict['raw_data'] = json.loads(job_dict['raw_data'])
                    except json.JSONDecodeError:
                        job_dict['raw_data'] = {}
                

                
                return job_dict
            return None
    
    def get_all_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all jobs with optional limit"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM jobs 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            jobs = []
            for row in cursor.fetchall():
                columns = [description[0] for description in cursor.description]
                job_dict = dict(zip(columns, row))
                
                # Deserialize JSON fields
                if job_dict.get('dataset'):
                    try:
                        job_dict['dataset'] = json.loads(job_dict['dataset'])
                    except json.JSONDecodeError:
                        job_dict['dataset'] = []
                
                if job_dict.get('sources'):
                    try:
                        job_dict['sources'] = json.loads(job_dict['sources'])
                    except json.JSONDecodeError:
                        job_dict['sources'] = []
                
                jobs.append(job_dict)
            
            return jobs
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM jobs WHERE job_id = ?', (job_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def cleanup_old_jobs(self, days: int = 30) -> int:
        """Delete jobs older than specified days"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM jobs 
                WHERE created_at < ?
            ''', (cutoff_date,))
            conn.commit()
            return cursor.rowcount
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total jobs
            total_jobs = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
            
            # Jobs by status
            status_counts = {}
            cursor = conn.execute('''
                SELECT status, COUNT(*) 
                FROM jobs 
                GROUP BY status
            ''')
            for status, count in cursor.fetchall():
                status_counts[status] = count
            
            # Recent jobs (last 24 hours)
            yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            recent_jobs = conn.execute('''
                SELECT COUNT(*) 
                FROM jobs 
                WHERE created_at >= ?
            ''', (yesterday,)).fetchone()[0]
            
            return {
                'total_jobs': total_jobs,
                'status_counts': status_counts,
                'recent_jobs_24h': recent_jobs
            }
    
    def rate_job(self, job_id: str, rating: str) -> bool:
        """Rate a job as 'good_dog' or 'bad_dog'"""
        if rating not in ['good_dog', 'bad_dog']:
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                UPDATE jobs 
                SET user_rating = ?, rating_timestamp = ?, updated_at = ?
                WHERE job_id = ?
            ''', (rating, datetime.now(), datetime.now(), job_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_job_rating_stats(self) -> Dict[str, Any]:
        """Get rating statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total rated jobs
            total_rated = conn.execute('''
                SELECT COUNT(*) FROM jobs WHERE user_rating IS NOT NULL
            ''').fetchone()[0]
            
            # Rating breakdown
            good_dogs = conn.execute('''
                SELECT COUNT(*) FROM jobs WHERE user_rating = 'good_dog'
            ''').fetchone()[0]
            
            bad_dogs = conn.execute('''
                SELECT COUNT(*) FROM jobs WHERE user_rating = 'bad_dog'
            ''').fetchone()[0]
            
            # Calculate percentage
            good_percentage = (good_dogs / total_rated * 100) if total_rated > 0 else 0
            bad_percentage = (bad_dogs / total_rated * 100) if total_rated > 0 else 0
            
            return {
                'total_rated': total_rated,
                'good_dogs': good_dogs,
                'bad_dogs': bad_dogs,
                'good_percentage': round(good_percentage, 1),
                'bad_percentage': round(bad_percentage, 1)
            }
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queries asked by users"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DISTINCT job_id, query, created_at, status, user_rating
                FROM jobs 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            queries = []
            for row in cursor.fetchall():
                job_id, query, created_at, status, user_rating = row
                queries.append({
                    'job_id': job_id,
                    'query': query,
                    'created_at': created_at,
                    'status': status,
                    'user_rating': user_rating
                })
            
            return queries
    
    def get_unique_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unique recent queries (no duplicates)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT query, MAX(created_at) as last_asked, COUNT(*) as times_asked
                FROM jobs 
                GROUP BY query
                ORDER BY last_asked DESC 
                LIMIT ?
            ''', (limit,))
            
            queries = []
            for row in cursor.fetchall():
                query, last_asked, times_asked = row
                queries.append({
                    'query': query,
                    'last_asked': last_asked,
                    'times_asked': times_asked
                })
            
            return queries 