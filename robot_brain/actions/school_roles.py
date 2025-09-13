"""
🏫 School Role Manager

Manages school-specific functions including patrol, student monitoring,
and administrative tasks. Handles role-based interactions and permissions.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class SchoolRoleManager:
    """
    🏫 School Role Manager
    
    Manages school-specific functions including:
    - Student monitoring and attendance
    - Patrol and security functions
    - Role-based access control
    - Administrative reporting
    """
    
    def __init__(self):
        """Initialize school role manager."""
        from ..core.config import config
        
        self.data_dir = config.DATA_DIR
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # School settings
        self.school_name = "Smart School"
        self.class_hours = {
            'start': '09:00',
            'end': '15:00',
            'break_start': '12:00',
            'break_end': '13:00'
        }
        
        # Role permissions
        self.role_permissions = {
            'student': ['ask_questions', 'request_help', 'entertainment'],
            'teacher': ['ask_questions', 'request_help', 'entertainment', 'take_photos', 'student_info'],
            'principal': ['ask_questions', 'request_help', 'entertainment', 'take_photos', 'student_info', 'reports', 'system_control'],
            'admin': ['all_permissions']
        }
        
        # Student database
        self.student_database = {}
        self.attendance_records = {}
        
        # Patrol settings
        self.patrol_routes = self._initialize_patrol_routes()
        self.patrol_status = 'idle'
        
        print("✅ School role manager initialized")
    
    def _initialize_patrol_routes(self) -> List[Dict[str, Any]]:
        """Initialize patrol routes for the school."""
        return [
            {
                'name': 'Main Corridor',
                'description': 'Primary hallway connecting classrooms',
                'priority': 'high',
                'last_patrol': None
            },
            {
                'name': 'Library Area',
                'description': 'Library and study areas',
                'priority': 'medium',
                'last_patrol': None
            },
            {
                'name': 'Playground',
                'description': 'Outdoor recreation area',
                'priority': 'medium',
                'last_patrol': None
            },
            {
                'name': 'Cafeteria',
                'description': 'Dining and food service area',
                'priority': 'low',
                'last_patrol': None
            }
        ]
    
    def check_permission(self, user_role: str, action: str) -> bool:
        """
        Check if user has permission for an action.
        
        Args:
            user_role: User's role
            action: Action to check
            
        Returns:
            True if permission granted
        """
        try:
            if user_role not in self.role_permissions:
                return False
            
            permissions = self.role_permissions[user_role]
            
            # Admin has all permissions
            if 'all_permissions' in permissions:
                return True
            
            # Check specific permission
            return action in permissions
            
        except Exception as e:
            print(f"❌ Permission check error: {e}")
            return False
    
    def register_student(self, name: str, student_id: str, grade: str, 
                        class_name: str, parent_contact: str = None) -> bool:
        """
        Register a new student.
        
        Args:
            name: Student's name
            student_id: Student ID
            grade: Grade level
            class_name: Class name
            parent_contact: Parent contact information
            
        Returns:
            True if registration successful
        """
        try:
            student_info = {
                'name': name,
                'student_id': student_id,
                'grade': grade,
                'class_name': class_name,
                'parent_contact': parent_contact,
                'registration_date': datetime.now().isoformat(),
                'attendance_count': 0,
                'last_seen': None
            }
            
            self.student_database[student_id] = student_info
            
            # Save to file
            self._save_student_database()
            
            print(f"✅ Student registered: {name} (ID: {student_id})")
            return True
            
        except Exception as e:
            print(f"❌ Student registration error: {e}")
            return False
    
    def record_attendance(self, student_id: str, status: str = 'present') -> bool:
        """
        Record student attendance.
        
        Args:
            student_id: Student ID
            status: Attendance status ('present', 'absent', 'late')
            
        Returns:
            True if recording successful
        """
        try:
            if student_id not in self.student_database:
                print(f"❌ Student not found: {student_id}")
                return False
            
            today = datetime.now().date().isoformat()
            
            if today not in self.attendance_records:
                self.attendance_records[today] = {}
            
            self.attendance_records[today][student_id] = {
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update student record
            if status == 'present':
                self.student_database[student_id]['attendance_count'] += 1
            
            self.student_database[student_id]['last_seen'] = datetime.now().isoformat()
            
            # Save records
            self._save_attendance_records()
            self._save_student_database()
            
            print(f"✅ Attendance recorded: {student_id} - {status}")
            return True
            
        except Exception as e:
            print(f"❌ Attendance recording error: {e}")
            return False
    
    def check_student_status(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Check student's current status.
        
        Args:
            student_id: Student ID
            
        Returns:
            Student status information or None if not found
        """
        try:
            if student_id not in self.student_database:
                return None
            
            student_info = self.student_database[student_id]
            today = datetime.now().date().isoformat()
            
            # Check today's attendance
            today_attendance = None
            if today in self.attendance_records:
                today_attendance = self.attendance_records[today].get(student_id)
            
            # Determine current status
            current_time = datetime.now().time()
            class_start = datetime.strptime(self.class_hours['start'], '%H:%M').time()
            class_end = datetime.strptime(self.class_hours['end'], '%H:%M').time()
            
            if class_start <= current_time <= class_end:
                if today_attendance and today_attendance['status'] == 'present':
                    status = 'in_class'
                elif today_attendance and today_attendance['status'] == 'late':
                    status = 'late'
                else:
                    status = 'absent'
            else:
                status = 'after_hours'
            
            return {
                'student_info': student_info,
                'current_status': status,
                'today_attendance': today_attendance,
                'attendance_count': student_info['attendance_count']
            }
            
        except Exception as e:
            print(f"❌ Student status check error: {e}")
            return None
    
    def start_patrol(self, route_name: str = None) -> bool:
        """
        Start patrol on specified route.
        
        Args:
            route_name: Name of patrol route
            
        Returns:
            True if patrol started successfully
        """
        try:
            if self.patrol_status == 'active':
                print("⚠️ Patrol already active")
                return False
            
            if route_name:
                route = next((r for r in self.patrol_routes if r['name'] == route_name), None)
                if not route:
                    print(f"❌ Route not found: {route_name}")
                    return False
            else:
                # Select highest priority route that hasn't been patrolled recently
                route = self._select_patrol_route()
            
            self.patrol_status = 'active'
            self.current_route = route
            
            # Record patrol start
            patrol_record = {
                'route_name': route['name'],
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self._save_patrol_record(patrol_record)
            
            print(f"🚶 Patrol started on route: {route['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Patrol start error: {e}")
            return False
    
    def end_patrol(self, observations: str = None) -> bool:
        """
        End current patrol.
        
        Args:
            observations: Patrol observations
            
        Returns:
            True if patrol ended successfully
        """
        try:
            if self.patrol_status != 'active':
                print("⚠️ No active patrol to end")
                return False
            
            # Update route last patrol time
            if hasattr(self, 'current_route'):
                for route in self.patrol_routes:
                    if route['name'] == self.current_route['name']:
                        route['last_patrol'] = datetime.now().isoformat()
                        break
            
            # Record patrol end
            patrol_record = {
                'route_name': self.current_route['name'],
                'end_time': datetime.now().isoformat(),
                'status': 'completed',
                'observations': observations or 'No observations'
            }
            
            self._save_patrol_record(patrol_record)
            
            self.patrol_status = 'idle'
            self.current_route = None
            
            print("✅ Patrol completed")
            return True
            
        except Exception as e:
            print(f"❌ Patrol end error: {e}")
            return False
    
    def _select_patrol_route(self) -> Dict[str, Any]:
        """Select the best route for patrol."""
        try:
            # Sort routes by priority and last patrol time
            sorted_routes = sorted(
                self.patrol_routes,
                key=lambda r: (
                    r['priority'] == 'high',  # High priority first
                    r['last_patrol'] is None,  # Never patrolled first
                    r['last_patrol'] or ''     # Then by last patrol time
                ),
                reverse=True
            )
            
            return sorted_routes[0]
            
        except Exception as e:
            print(f"❌ Route selection error: {e}")
            return self.patrol_routes[0]
    
    def generate_attendance_report(self, date: str = None, class_name: str = None) -> Dict[str, Any]:
        """
        Generate attendance report.
        
        Args:
            date: Report date (YYYY-MM-DD format)
            class_name: Specific class to report on
            
        Returns:
            Attendance report data
        """
        try:
            if not date:
                date = datetime.now().date().isoformat()
            
            report_data = {
                'date': date,
                'class_name': class_name,
                'total_students': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'attendance_rate': 0.0,
                'students': []
            }
            
            if date in self.attendance_records:
                attendance_data = self.attendance_records[date]
                
                for student_id, attendance in attendance_data.items():
                    student_info = self.student_database.get(student_id)
                    
                    if not student_info:
                        continue
                    
                    # Filter by class if specified
                    if class_name and student_info['class_name'] != class_name:
                        continue
                    
                    report_data['students'].append({
                        'student_id': student_id,
                        'name': student_info['name'],
                        'class_name': student_info['class_name'],
                        'status': attendance['status'],
                        'timestamp': attendance['timestamp']
                    })
                    
                    # Count statuses
                    if attendance['status'] == 'present':
                        report_data['present'] += 1
                    elif attendance['status'] == 'absent':
                        report_data['absent'] += 1
                    elif attendance['status'] == 'late':
                        report_data['late'] += 1
                
                report_data['total_students'] = len(report_data['students'])
                
                if report_data['total_students'] > 0:
                    report_data['attendance_rate'] = (
                        (report_data['present'] + report_data['late']) / 
                        report_data['total_students']
                    )
            
            # Save report
            self._save_report('attendance', report_data)
            
            return report_data
            
        except Exception as e:
            print(f"❌ Attendance report error: {e}")
            return {}
    
    def get_school_status(self) -> Dict[str, Any]:
        """Get current school status."""
        try:
            current_time = datetime.now()
            current_date = current_time.date().isoformat()
            
            # Check if school is in session
            class_start = datetime.strptime(self.class_hours['start'], '%H:%M').time()
            class_end = datetime.strptime(self.class_hours['end'], '%H:%M').time()
            current_time_only = current_time.time()
            
            in_session = class_start <= current_time_only <= class_end
            
            # Get today's attendance summary
            today_attendance = self.attendance_records.get(current_date, {})
            present_count = sum(1 for a in today_attendance.values() if a['status'] == 'present')
            absent_count = sum(1 for a in today_attendance.values() if a['status'] == 'absent')
            late_count = sum(1 for a in today_attendance.values() if a['status'] == 'late')
            
            return {
                'school_name': self.school_name,
                'current_time': current_time.isoformat(),
                'in_session': in_session,
                'patrol_status': self.patrol_status,
                'total_students': len(self.student_database),
                'today_attendance': {
                    'present': present_count,
                    'absent': absent_count,
                    'late': late_count,
                    'total': len(today_attendance)
                },
                'patrol_routes': len(self.patrol_routes)
            }
            
        except Exception as e:
            print(f"❌ School status error: {e}")
            return {}
    
    def _save_student_database(self):
        """Save student database to file."""
        try:
            db_path = self.data_dir / "student_database.json"
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(self.student_database, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Student database save error: {e}")
    
    def _save_attendance_records(self):
        """Save attendance records to file."""
        try:
            records_path = self.data_dir / "attendance_records.json"
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Attendance records save error: {e}")
    
    def _save_patrol_record(self, record: Dict[str, Any]):
        """Save patrol record to file."""
        try:
            patrol_path = self.reports_dir / f"patrol_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Load existing records
            if patrol_path.exists():
                with open(patrol_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            else:
                records = []
            
            records.append(record)
            
            with open(patrol_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Patrol record save error: {e}")
    
    def _save_report(self, report_type: str, data: Dict[str, Any]):
        """Save report to file."""
        try:
            report_path = self.reports_dir / f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Report save error: {e}")
    
    def get_school_info(self) -> Dict[str, Any]:
        """Get school information and statistics."""
        return {
            'school_name': self.school_name,
            'class_hours': self.class_hours,
            'role_permissions': self.role_permissions,
            'patrol_routes': self.patrol_routes,
            'total_students': len(self.student_database),
            'total_attendance_records': sum(len(records) for records in self.attendance_records.values())
        }