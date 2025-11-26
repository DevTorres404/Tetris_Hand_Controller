import unittest
from unittest.mock import MagicMock, patch
import sys
import time

# Mock external dependencies before importing the module under test
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
sys.modules['mediapipe.solutions'] = MagicMock()

# Now we can import the module
from src.controlador_manos import ControladorMano

class TestControladorMano(unittest.TestCase):
    def setUp(self):
        # Setup common mocks
        self.mock_cv2 = sys.modules['cv2']
        self.mock_mp = sys.modules['mediapipe']
        
        # Mock VideoCapture
        self.mock_cap = MagicMock()
        self.mock_cv2.VideoCapture.return_value = self.mock_cap
        self.mock_cap.read.return_value = (True, MagicMock())
        
        # Mock MediaPipe Hands
        self.mock_hands_instance = MagicMock()
        self.mock_mp.solutions.hands.Hands.return_value = self.mock_hands_instance
        
        # Initialize controller with camera disabled to avoid window creation
        self.controller = ControladorMano(mostrar_camara=False)

    def tearDown(self):
        self.controller.detener()

    def test_initialization(self):
        """Test that the controller initializes correctly."""
        self.assertIsNotNone(self.controller)
        self.mock_cv2.VideoCapture.assert_called()
        self.mock_mp.solutions.hands.Hands.assert_called()

    def test_consultar_default(self):
        """Test consultar returns default values when no gestures are detected."""
        # Setup empty results
        self.mock_hands_instance.process.return_value.multi_hand_landmarks = None
        
        # Run one loop iteration manually (since we are not threading in test)
        # We need to simulate the _bucle logic partially or test helper methods directly
        # Since _bucle is an infinite loop, we can't call it directly.
        # Instead, we will test the helper methods that process logic.
        
        dir_mov, caida_suave, rotar, caida_dura = self.controller.consultar()
        self.assertEqual(dir_mov, 0)
        self.assertFalse(caida_suave)
        self.assertFalse(rotar)
        self.assertFalse(caida_dura)

    def test_pulgar_arriba_abajo(self):
        """Test thumb direction detection logic."""
        # Create mock landmarks
        lm = [MagicMock() for _ in range(21)]
        
        # Setup for Thumb UP
        # Tip (4) above MCP (2) -> y decreases (screen coords)
        lm[4].y = 0.1
        lm[2].y = 0.3  # diff = -0.2 (negative is up)
        lm[4].x = 0.5
        lm[2].x = 0.5
        lm[3].y = 0.2 # IP between tip and MCP
        
        # Inject threshold
        self.controller.umbral_dir_pulgar = 0.1
        
        arriba, abajo = self.controller._pulgar_arriba_abajo(lm)
        self.assertTrue(arriba)
        self.assertFalse(abajo)
        
        # Setup for Thumb DOWN
        lm[4].y = 0.5
        lm[2].y = 0.3 # diff = 0.2 (positive is down)
        lm[3].y = 0.4
        
        arriba, abajo = self.controller._pulgar_arriba_abajo(lm)
        self.assertFalse(arriba)
        self.assertTrue(abajo)

    def test_contar_dedos_extendidos(self):
        """Test finger extension detection."""
        lm = [MagicMock() for _ in range(21)]
        
        # Setup Index finger extended
        # Tip (8) above PIP (6)
        lm[8].y = 0.1
        lm[6].y = 0.3
        # Distance check
        lm[8].x = 0.5
        lm[0].x = 0.5 # wrist
        lm[0].y = 0.9
        
        # Mock _es_dedo_extendido to return True for index, False for others for simplicity
        with patch.object(self.controller, '_es_dedo_extendido', side_effect=[True, False, False, False]):
            ind, med, anl, men = self.controller._contar_dedos_extendidos(lm)
            self.assertTrue(ind)
            self.assertFalse(med)

    def test_consultar_resets_flags(self):
        """Test that consultar resets one-shot flags."""
        self.controller.borde_rotar_hor = True
        self.controller.borde_caida_dura = True
        
        _, _, rotar, caida_dura = self.controller.consultar()
        
        self.assertTrue(rotar)
        self.assertTrue(caida_dura)
        
        # Second call should be False
        _, _, rotar, caida_dura = self.controller.consultar()
        self.assertFalse(rotar)
        self.assertFalse(caida_dura)

if __name__ == '__main__':
    unittest.main()
