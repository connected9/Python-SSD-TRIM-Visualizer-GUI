# trimvision/ui/lba_grid_widget.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QTimer
from trimvision import config
from trimvision.core.logger import logger

# Define block states (could be an Enum for more robustness)
STATE_NON_PROCEEDED = 0
STATE_PROCESSING = 1
STATE_PROCESSED = 2
STATE_BLOCKED = 3

class LbaGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200) # Ensure it has some default size

        self.grid_rows = 20
        self.grid_cols = 30 # Results in 600 blocks, adjust as needed
        self.total_visual_blocks = self.grid_rows * self.grid_cols

        self.block_states = []
        self.block_colors = {
            STATE_NON_PROCEEDED: QColor(*config.COLOR_LBA_NON_PROCEEDED),
            STATE_PROCESSING: QColor(*config.COLOR_LBA_PROCESSING),
            STATE_PROCESSED: QColor(*config.COLOR_LBA_PROCESSED),
            STATE_BLOCKED: QColor(*config.COLOR_LBA_BLOCKED),
        }
        
        # For animation (simple pulse for processing block)
        self._processing_block_index = -1
        self._processing_pulse_state = False
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._toggle_pulse_state)
        self._pulse_interval = 300 # ms

        self.block_padding = 1 # pixels between blocks
        self.block_corner_radius = 2 # pixels for rounded corners

        self.total_worker_chunks = 100 # Default, will be updated by initialize_grid

        self.reset_grid() # Initialize with default states

    def initialize_grid(self, total_drive_capacity_gb: float, total_worker_chunks: int):
        logger.info(f"Initializing LBA grid: {self.grid_rows}x{self.grid_cols} blocks. Worker chunks: {total_worker_chunks}")
        self.total_worker_chunks = total_worker_chunks if total_worker_chunks > 0 else 100
        self.reset_grid()
        self.update() # Trigger repaint

    def reset_grid(self):
        self.block_states = [STATE_NON_PROCEEDED] * self.total_visual_blocks
        self._stop_processing_animation()
        self.update()

    def _map_worker_chunk_to_visual_blocks(self, worker_chunk_index: int):
        """Maps a worker chunk index to a range of visual block indices."""
        if self.total_worker_chunks <= 0 or self.total_visual_blocks <= 0:
            return []

        # Calculate how many visual blocks this worker chunk represents
        start_ratio = worker_chunk_index / self.total_worker_chunks
        end_ratio = (worker_chunk_index + 1) / self.total_worker_chunks

        start_visual_block = int(start_ratio * self.total_visual_blocks)
        end_visual_block = int(end_ratio * self.total_visual_blocks) -1 # Inclusive end

        # Ensure end_visual_block doesn't exceed total_visual_blocks due to rounding
        end_visual_block = min(end_visual_block, self.total_visual_blocks - 1)
        
        if start_visual_block > end_visual_block: # Can happen if one worker chunk covers less than one visual block
            return [start_visual_block] if start_visual_block < self.total_visual_blocks else []
            
        return list(range(start_visual_block, end_visual_block + 1))


    def update_worker_chunk_state(self, worker_chunk_index: int, state_str: str):
        """
        Updates the visual blocks corresponding to a worker chunk.
        state_str: "Processing", "Processed", "Blocked"
        """
        new_state = STATE_NON_PROCEEDED
        if state_str == "Processing":
            new_state = STATE_PROCESSING
        elif state_str == "Processed":
            new_state = STATE_PROCESSED
        elif state_str == "Blocked":
            new_state = STATE_BLOCKED
        else:
            logger.warning(f"Unknown state string received: {state_str}")
            return

        visual_block_indices = self._map_worker_chunk_to_visual_blocks(worker_chunk_index)

        if new_state == STATE_PROCESSING and visual_block_indices:
            # For "Processing", typically highlight the first block in the range
            self._start_processing_animation(visual_block_indices[0])
        else:
            # If not processing, or if processing covers multiple blocks, clear old animation
            self._stop_processing_animation()

        changed = False
        for vb_idx in visual_block_indices:
            if 0 <= vb_idx < self.total_visual_blocks:
                if self.block_states[vb_idx] != new_state:
                    self.block_states[vb_idx] = new_state
                    changed = True
            else:
                logger.warning(f"Visual block index {vb_idx} out of range for worker chunk {worker_chunk_index}")
        
        if changed:
            self.update() # Trigger repaint

    def _start_processing_animation(self, block_index: int):
        if self._processing_block_index != block_index:
            self._stop_processing_animation() # Stop previous if any
        self._processing_block_index = block_index
        self._processing_pulse_state = True # Start in "bright" state
        if not self._pulse_timer.isActive():
            self._pulse_timer.start(self._pulse_interval) # <<< CORRECTED HERE
        self.update() # Update immediately for the new processing block

    def _stop_processing_animation(self):
        if self._pulse_timer.isActive():
            self._pulse_timer.stop()
        # Restore the original color of the previously processing block if it's not the new one
        if self._processing_block_index != -1:
            # Assuming it should revert to NON_PROCEEDED if animation stops,
            # or better, its actual last committed state before "Processing"
            # For now, let the main state update handle its final color.
            pass 
        self._processing_block_index = -1
        self.update()

    def _toggle_pulse_state(self):
        self._processing_pulse_state = not self._processing_pulse_state
        if self._processing_block_index != -1:
            self.update() # Repaint only the affected block area later for optimization

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        widget_width = self.width()
        widget_height = self.height()

        if widget_width <= 0 or widget_height <= 0 or self.grid_cols == 0 or self.grid_rows == 0:
            return

        # Calculate block size based on available space and padding
        total_padding_width = (self.grid_cols + 1) * self.block_padding
        total_padding_height = (self.grid_rows + 1) * self.block_padding

        block_w = (widget_width - total_padding_width) / self.grid_cols
        block_h = (widget_height - total_padding_height) / self.grid_rows

        if block_w <= 0 or block_h <= 0: # Not enough space to draw
            # Optionally draw a "Too small" message
            # painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Grid too small to render")
            return

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                block_index = r * self.grid_cols + c
                if block_index >= len(self.block_states): continue # Should not happen

                state = self.block_states[block_index]
                color = self.block_colors.get(state, QColor(Qt.GlobalColor.black)) # Default to black if state unknown

                # Pulsing effect for the currently processing block
                if block_index == self._processing_block_index:
                    if self._processing_pulse_state:
                        # Make it slightly brighter or use a distinct border
                        # For simplicity, let's make it slightly brighter by reducing alpha of others or enhancing this one
                        # color = color.lighter(120) # Simple lighter effect
                        # Or change border:
                        pen = QPen(color.darker(150), 1.5) # Distinct border for processing
                    else:
                        # color = color.darker(110) # Slightly darker for the other pulse state
                        pen = QPen(color, 0.5) # Normal border
                else:
                    pen = QPen(color.darker(110), 0.5) # Default border slightly darker than fill

                painter.setPen(pen)
                painter.setBrush(QBrush(color))

                x = self.block_padding + c * (block_w + self.block_padding)
                y = self.block_padding + r * (block_h + self.block_padding)
                
                rect = QRectF(x, y, block_w, block_h)
                painter.drawRoundedRect(rect, self.block_corner_radius, self.block_corner_radius)

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update() # Redraw on resize