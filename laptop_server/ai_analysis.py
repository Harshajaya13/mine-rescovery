class AIAnalyzer:
    def __init__(self, mapper):
        self.mapper = mapper
        
    def analyze_situation(self, telemetry, yolo_detections):
        """
        Takes sensor telemetry and camera detections to generate a report.
        """
        gas = telemetry.get('gas_detected', 0)
        dist = telemetry.get('distance_cm', 100)
        rssi = telemetry.get('rssi', -50)
        
        report = {
            'status': 'Normal',
            'message': 'Conditions stable. Continuing exploration.',
            'hazards': [],
            'suggested_action': 'continue'
        }
        
        hazards = []
        
        # Rule 1: Gas Detection
        if gas == 1:
            report['status'] = 'CRITICAL'
            hazards.append('Toxic gas leak detected!')
            report['suggested_action'] = 'evacuate'
            
        # Rule 2: Obstacle/Debris
        if dist < 20:
            hazards.append(f'Obstacle detected at {dist}cm.')
            if report['suggested_action'] != 'evacuate':
                report['suggested_action'] = 'reroute'
                report['status'] = 'WARNING'
                
        # Rule 3: Visual hazards from YOLO (e.g. fire, person)
        if 'person' in yolo_detections:
            report['status'] = 'ALERT'
            hazards.append('Possible trapped worker identified!')
            report['suggested_action'] = 'halt_and_wait_for_operator'
            
        # Rule 4: Signal Strength
        if rssi < -80:
            hazards.append('Warning: Weak communication signal.')
            if report['suggested_action'] == 'continue':
                report['suggested_action'] = 'return_to_signal'
                report['status'] = 'WARNING'
                
        if hazards:
            report['hazards'] = hazards
            report['message'] = ' | '.join(hazards)
            
        # Update map based on findings
        current_loc = self.mapper.get_current_location()
        if report['status'] == 'CRITICAL':
            self.mapper.mark_section(current_loc, 'hazardous')
        elif report['status'] == 'Normal':
            self.mapper.mark_section(current_loc, 'safe')
            
        return report
