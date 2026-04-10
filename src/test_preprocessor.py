import sys
import os

# Add the project root to sys.path to allow relative imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessor import TextPreprocessor

def test_basic_splitting():
    tp = TextPreprocessor()
    sample = '그는 하늘을 보며 말했다. "정말 아름다운 밤이군요." 그러자 그녀가 웃었다.'
    
    segments = tp.process_story(sample)
    
    print(f"Sample: {sample}")
    print(f"Resulting segments: {len(segments)}")
    for seg in segments:
        print(f" - {seg}")
    
    assert segments[0].type == "narrative"
    assert segments[1].type == "dialogue"
    assert segments[2].type == "narrative"
    print("✅ Basic splitting test passed!")

def test_multi_line_splitting():
    tp = TextPreprocessor()
    sample = """
    용사는 칼을 뽑았다.
    "물러서라, 마왕!"
    그의 외침이 동굴에 울려 퍼졌다.
    """
    
    segments = tp.process_story(sample)
    
    print(f"\nMulti-line Sample processing...")
    for seg in segments:
        print(f" - {seg}")
        
    assert len(segments) == 3
    assert segments[1].text == '"물러서라, 마왕!"'
    print("✅ Multi-line splitting test passed!")

if __name__ == "__main__":
    print("--- Testing TextPreprocessor ---")
    try:
        test_basic_splitting()
        test_multi_line_splitting()
        print("\n--- All Tests Passed! ---")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
