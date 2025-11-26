import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Mock dependencies before importing cascara_tetris
sys.modules['pygame'] = MagicMock()
# We don't mock urllib here to avoid conflicts, we'll patch it where used or patch the import
sys.modules['numpy'] = MagicMock()
sys.modules['core_tetris'] = MagicMock()
sys.modules['controlador_manos'] = MagicMock()

# Import module under test
# We need to make sure urllib.request is available or mocked if it's imported at top level
# cascara_tetris imports urllib.request. 
# Let's mock it in sys.modules just to be safe for the import
mock_urllib_request = MagicMock()
sys.modules['urllib.request'] = mock_urllib_request
sys.modules['urllib'] = MagicMock()
sys.modules['urllib'].request = mock_urllib_request

from src.cascara_tetris import GestorAudio, RenderizadorTetris, COLORES_PIEZAS

class TestGestorAudio(unittest.TestCase):
    def setUp(self):
        self.mock_pygame = sys.modules['pygame']
        # Reset the mock for each test
        mock_urllib_request.reset_mock()
        
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_initialization_downloads_sounds(self, mock_file, mock_makedirs, mock_exists):
        """Test that audio manager attempts to download sounds if missing."""
        # Simulate directory missing, then file missing for all files
        # There are 8 files. 
        # First check: directory exists? -> False
        # Then loop 8 times: file exists? -> False
        # So we need 9 False values.
        mock_exists.side_effect = [False] + [False] * 8
        
        # Mock urlopen context manager
        mock_response = MagicMock()
        mock_response.read.return_value = b'fake_audio_data'
        
        # Configure the mock to return the response when called
        mock_urllib_request.urlopen.return_value.__enter__.return_value = mock_response
        
        gestor = GestorAudio()
        
        # Should attempt to create directory
        mock_makedirs.assert_called()
        
        # Should attempt to download files
        # We expect 8 calls to urlopen
        self.assertEqual(mock_urllib_request.urlopen.call_count, 8)
        self.assertTrue(mock_file.called)

    def test_reproducir(self):
        """Test playing a sound."""
        # We need to mock _descargar_y_cargar_sonidos to avoid constructor logic
        with patch.object(GestorAudio, '_descargar_y_cargar_sonidos'):
            gestor = GestorAudio()
            gestor.sonidos = {'test.wav': MagicMock()}
            gestor.audio_disponible = True
            
            gestor.reproducir('test.wav')
            gestor.sonidos['test.wav'].play.assert_called()

class TestRenderizadorTetris(unittest.TestCase):
    def setUp(self):
        self.mock_screen = MagicMock()
        self.renderer = RenderizadorTetris(self.mock_screen)
        
    def test_dibujar_tablero(self):
        """Test drawing the board."""
        # Create a mock board (20x10)
        tablero = [[None for _ in range(10)] for _ in range(20)]
        tablero[19][0] = "I" # One block
        
        self.renderer.dibujar_tablero(tablero)
        
        # Should draw background and blocks
        self.assertTrue(self.mock_screen.fill.called)
        self.assertTrue(sys.modules['pygame'].draw.rect.called)

    def test_dibujar_pieza(self):
        """Test drawing a piece."""
        mock_pieza = MagicMock()
        mock_pieza.tipo = "T"
        mock_pieza.celdas.return_value = [(5, 5), (5, 6), (4, 6), (6, 6)]
        
        self.renderer.dibujar_pieza(mock_pieza)
        
        self.assertTrue(sys.modules['pygame'].draw.rect.called)

    def test_dibujar_hud(self):
        """Test drawing the HUD."""
        estado = {
            'puntaje': 100,
            'lineas': 4,
            'nivel': 2
        }
        self.renderer.dibujar_hud(estado, mano_activa=True)
        
        # Should verify blit calls for text
        self.assertTrue(self.mock_screen.blit.called)

if __name__ == '__main__':
    unittest.main()

