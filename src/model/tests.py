import unittest

class Rectangle():
    def __init__(self, height = 5, width = 10) -> None:
        self._height = None
        self._width = None
        self.SetHeight( height )
        self.SetWidth( width )
 
    @property
    def width(self):
        return self._width

    def GetWidth(self):
        return self._width
    
    def GetHeight(self):
        return self._height
    
    def SetHeight(self, value):
        if  value <= 0 :
            raise ValueError('Height is not positive')
        self._height = value
    
    def SetWidth(self, value):        
        if  value <= 0:
            raise ValueError('Width is not positive')
        self._width = value

    def GetArea(self):
        return self._width * self._height
    
class TestRectangleClass(unittest.TestCase):
    def test_RectangleExemplarCreation(self):
        with self.assertRaises(ValueError):
            Rectangle(-1,4)
        with self.assertRaises(ValueError):
            Rectangle(1,0)

    def setUp(self):
        self.figure = Rectangle()

    def test_GetWidth(self):
        self.figure.SetWidth(4)
        self.assertEqual(self.figure.GetWidth(), 4, 'GetWidth returned wrong value.')

    def test_WidthProperty(self):
        self.figure.SetWidth(4)
        self.assertEqual(self.figure.width, 4, 'Width property has wrong value.')

    def test_GetHeight(self):
        self.figure.SetHeight(7)
        self.assertEqual(self.figure.GetHeight(), 7, 'GetHeight returned wrong value.')

    def test_GetArea(self):
        figure = Rectangle(4,6)
        self.assertEqual(figure.GetArea(), 4*6, 'GetArea return wrong area.')



unittest.main()