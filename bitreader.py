# Least-significant bit first

class BitReader():
    def __init__(self, data):
        self.data = data
        self.bit_index = 0
        self.pos = 0
        
    def read_bit(self):
        bit = self.data[self.pos] >> self.bit_index & 1 # Right-shift the bit to the least-significant position, then mask (bit-wise AND) to extract it

        self.bit_index += 1
        
        if self.bit_index > 7:
            self.bit_index = 0
            self.pos += 1
            
        
        return bit
        
        
        
    def read_bits(self, count):
        result = 0
        
        for c in range(count):
            bit = self.read_bit()
            
            # Left-shift to make space for a new bit, then (bit-wise OR) to accumulate it to the result
            result = result | bit << c
            
            
            
        return result
        
        
    
    
    def seek(self, bit_position):
        self.pos = bit_position // 8
        self.bit_index = bit_position % 8
