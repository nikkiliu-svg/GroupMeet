/**
 * When2meet-style calendar component for availability selection.
 */

class AvailabilityCalendar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedSlots = new Set();
        this.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        this.timeSlots = [
            '8am-10am',
            '10am-12pm',
            '12pm-2pm',
            '2pm-4pm',
            '4pm-6pm',
            '6pm-8pm'
        ];
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        let html = '<table class="calendar-grid"><thead><tr><th></th>';
        
        // Header row with days
        this.days.forEach(day => {
            html += `<th>${day}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        // Time slot rows
        this.timeSlots.forEach(timeSlot => {
            html += `<tr><td class="time-label">${timeSlot}</td>`;
            this.days.forEach(day => {
                const slotId = `${day}-${timeSlot}`;
                html += `<td class="calendar-cell" data-slot="${slotId}"></td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        this.container.innerHTML = html;
    }

    attachEventListeners() {
        const cells = this.container.querySelectorAll('.calendar-cell');
        cells.forEach(cell => {
            cell.addEventListener('click', () => {
                this.toggleSlot(cell);
            });
            
            cell.addEventListener('mouseenter', () => {
                if (!cell.classList.contains('selected')) {
                    cell.classList.add('hover');
                }
            });
            
            cell.addEventListener('mouseleave', () => {
                cell.classList.remove('hover');
            });
        });
    }

    toggleSlot(cell) {
        const slotId = cell.getAttribute('data-slot');
        
        if (this.selectedSlots.has(slotId)) {
            this.selectedSlots.delete(slotId);
            cell.classList.remove('selected');
        } else {
            this.selectedSlots.add(slotId);
            cell.classList.add('selected');
        }
    }

    getSelectedSlots() {
        // Convert to array of "Day TimeSlot" format
        return Array.from(this.selectedSlots).map(slot => {
            const [day, timeSlot] = slot.split('-');
            return `${day} ${timeSlot}`;
        });
    }

    setSelectedSlots(slots) {
        // Clear current selection
        this.selectedSlots.clear();
        const cells = this.container.querySelectorAll('.calendar-cell');
        cells.forEach(cell => {
            cell.classList.remove('selected');
        });
        
        // Set new selection
        slots.forEach(slot => {
            // Convert "Day TimeSlot" to "Day-TimeSlot" format
            const normalized = slot.replace(' ', '-');
            this.selectedSlots.add(normalized);
            
            const cell = this.container.querySelector(`[data-slot="${normalized}"]`);
            if (cell) {
                cell.classList.add('selected');
            }
        });
    }

    clear() {
        this.selectedSlots.clear();
        const cells = this.container.querySelectorAll('.calendar-cell');
        cells.forEach(cell => {
            cell.classList.remove('selected');
        });
    }
}

// Export class
window.AvailabilityCalendar = AvailabilityCalendar;

