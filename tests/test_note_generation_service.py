import os
import sys
import json
import pytest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.note_generation_service import NoteGenerationService



@pytest.fixture

def transcript_file(tmp_path):

    p = tmp_path / "transcript.txt"

    p.write_text("This is the transcript.")

    return str(p)



@pytest.fixture

def output_md(tmp_path):

    return str(tmp_path / "notes.md")



@patch('src.gemini_api_wrapper.GeminiAPIWrapper.generate_content')



def test_generate_success(mock_gen, transcript_file, output_md):



    """Test successful note generation."""



    mock_gen.return_value = "# Notes\nContent"



    



    success = NoteGenerationService.generate(



        transcript_path=transcript_file,



        output_path=output_md



    )



    



    assert success is True



    



    # Verify call structure



    kwargs = mock_gen.call_args[1]



    assert "This is the transcript." in kwargs['prompt']



    assert "You are a notes-generation agent." in kwargs['system_instruction']



    



    with open(output_md, 'r') as f:



        assert f.read() == "# Notes\nContent"







@patch('src.gemini_api_wrapper.GeminiAPIWrapper.generate_content')



def test_generate_custom_prompt(mock_gen, transcript_file, output_md):



    """Test note generation with custom prompt text."""



    mock_gen.return_value = "Custom output"



    



    custom_prompt = "Custom base prompt"



    success = NoteGenerationService.generate(



        transcript_path=transcript_file,



        output_path=output_md,



        prompt_text=custom_prompt



    )



    



    assert success is True



    kwargs = mock_gen.call_args[1]



    assert kwargs['system_instruction'] == "Custom base prompt"



    assert "This is the transcript." in kwargs['prompt']
