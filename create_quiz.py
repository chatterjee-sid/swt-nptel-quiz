import re
import html
import json  # <-- Added for embedding the answer key

# --- Configuration ---
MARKDOWN_FILE = "Assignments.md"
HTML_FILE = "quiz.html"
# ---------------------

def create_html_quiz(md_file, html_file):
    print(f"Reading '{md_file}'...")
    try:
        with open(md_file, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()
    except FileNotFoundError:
        print(f"--- ERROR ---")
        print(f"File not found: '{md_file}'")
        print("Please make sure your markdown file is in the same directory and named correctly.")
        print(f"---------------")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # This dictionary will store the correct answers
    correct_answers = {}

    with open(html_file, 'w', encoding='utf-8') as f_out:
        # --- HTML Boilerplate and CSS Styling ---
        f_out.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Software Testing Quiz</title>
  <style>
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
      margin: 0 auto; 
      max-width: 900px;
      padding: 1em;
      line-height: 1.6; 
      background-color: #f9f9f9; 
    }
    h1 { 
      color: #222; 
      border-bottom: 2px solid #007BFF; 
      padding-bottom: 10px; 
    }
    .question-block { 
      margin-bottom: 2em; 
      background-color: #fff; 
      border: 1px solid #ddd; 
      padding: 1.5em; 
      border-radius: 8px; 
      box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    }
    .question-block h3 { 
      margin-top: 0; 
      color: #0056b3; 
    }
    .directions { 
      background-color: #e6f7ff; 
      border: 1px solid #b3e0ff; 
      padding: 0.1em 1.5em; 
      border-radius: 8px; 
      margin-bottom: 1em; 
    }
    label { 
      display: block; 
      margin: 0.75em 0 0.75em 0.5em; 
      padding: 0.5em; 
      border-radius: 5px; 
      cursor: pointer; 
      transition: background-color 0.2s; 
    }
    label:hover { 
      background-color: #f0f8ff; 
    }
    input[type='radio'] { 
      margin-right: 10px; 
      transform: scale(1.1);
    }
    img { 
      max-width: 100%; 
      height: auto; 
      border: 1px solid #ccc; 
      border-radius: 5px; 
      margin-top: 1em; 
    }
    pre { 
      background-color: #2d2d2d; 
      color: #f1f1f1; 
      padding: 1em; 
      border-radius: 5px; 
      overflow-x: auto; 
    }
    .submit-btn { 
      display: block;
      margin: 2em auto;
      background-color: #007BFF; 
      color: white; 
      padding: 12px 25px; 
      border: none; 
      border-radius: 5px; 
      cursor: pointer; 
      font-size: 18px; 
      font-weight: bold; 
    }
    .submit-btn:hover { 
      background-color: #0056b3; 
    }
    /* --- NEW STYLES FOR GRADING --- */
    #results {
      padding: 1em;
      margin: 2em 0;
      border-radius: 8px;
      text-align: center;
      background-color: #e6f7ff;
      border: 1px solid #b3e0ff;
      font-size: 1.5em;
      font-weight: bold;
      color: #0056b3;
    }
    .correct {
      background-color: #d4edda !important;
      border: 1px solid #c3e6cb;
      font-weight: bold;
    }
    .incorrect {
      background-color: #f8d7da !important;
      border: 1px solid #f5c6cb;
    }
  </style>
</head>
<body>
  <h1>Software Testing Quiz</h1>
  <div id="results" style="display: none;"></div>
  
  <form id="quizForm" onsubmit="handleSubmit(event)">
""")

        # --- Parsing Logic ---
        question_number = 0
        in_code_block = False
        in_question_block = False

        for line in lines:
            stripped = line.strip()

            if not stripped: 
                continue

            # Handle code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                f_out.write("<pre><code>\n" if in_code_block else "</code></pre>\n")
                continue
            
            if in_code_block:
                f_out.write(html.escape(line))
                continue

            # Handle Main Title
            if stripped.startswith('## '):
                continue
            
            # Handle Directions
            dirn_match = re.match(r'### (DIRN .*)', stripped)
            if dirn_match:
                if in_question_block: 
                    f_out.write("</div>\n") # Close previous block
                f_out.write(f"\n<div class='directions'>\n  <h4>{dirn_match.group(1)}</h4>\n")
                in_question_block = True
                question_number = 0 
                continue 

            # Handle Questions
            q_match = re.match(r'### (\d+)\. (.*)', stripped)
            if q_match:
                if in_question_block: 
                    f_out.write("</div>\n") # Close previous block
                
                question_number = q_match.group(1)
                question_text = q_match.group(2)
                f_out.write(f"\n<div class='question-block'>\n")
                f_out.write(f"  <h3>Question {question_number}: {html.escape(question_text)}</h3>\n")
                in_question_block = True
                continue 

            # Handle Options
            opt_match = re.match(r'- (A|B|C|D|E|F)\. (.*)', stripped)
            if opt_match and question_number != 0:
                option_letter = opt_match.group(1)
                option_full_text = opt_match.group(2)
                
                # --- NEW: Check for answer and store it ---
                is_correct = '✅' in option_full_text
                if is_correct:
                    correct_answers[question_number] = option_letter
                
                # Clean the answer (remove markdown bold and checkmark)
                option_text = re.sub(r'\*\*?(.*?)\*\*? ?(✅)?', r'\1', option_full_text)
                
                # --- NEW: Added an 'id' to the label for styling ---
                f_out.write(f"  <label for='q{question_number}_{option_letter}' id='label-q{question_number}-{option_letter}'>\n")
                f_out.write(f"    <input type='radio' name='q{question_number}' id='q{question_number}_{option_letter}' value='{option_letter}'>\n")
                f_out.write(f"    {html.escape(option_text)}\n")
                f_out.write("  </label>\n")
                continue

            # Handle Images
            img_match = re.match(r'!\[image\]\((.*)\)', stripped)
            if img_match:
                img_src = img_match.group(1)
                f_out.write(f"  <p><img src='{img_src}' alt='Quiz Image for question {question_number}'></p>\n")
                continue
            
            # Handle prose lines
            if in_question_block and not (q_match or dirn_match or opt_match or img_match):
                prose_text = stripped.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                f_out.write(f"  <p>{prose_text}</p>\n")
        
        # --- Clean up ---
        if in_question_block: 
            f_out.write("</div>\n") # Close the very last block
        
        f_out.write("\n<button type='submit' class='submit-btn'>Submit & Grade</button>\n")
        f_out.write("  </form>\n")
        
        # --- NEW: Embed Answer Key and Grading Script ---
        
        # 1. Embed the answer key as a JavaScript object
        f_out.write(f"<script>\nconst correctAnswers = {json.dumps(correct_answers, indent=2)};\n</script>\n")
        
        # 2. Add the grading function
        f_out.write("""
<script>
function handleSubmit(event) {
  event.preventDefault(); // Stop the form from reloading the page
  
  let score = 0;
  const totalQuestions = Object.keys(correctAnswers).length;

  // Clear all previous formatting
  document.querySelectorAll('label').forEach(label => {
    label.classList.remove('correct', 'incorrect');
  });

  // Loop through each question in the answer key
  for (const qNum in correctAnswers) {
    const correctLetter = correctAnswers[qNum];
    const correctLabel = document.getElementById(`label-q${qNum}-${correctLetter}`);
    
    // Find what the user selected
    const userAnswerInput = document.querySelector(`input[name='q${qNum}']:checked`);
    
    if (userAnswerInput) {
      const userLetter = userAnswerInput.value;
      const userLabel = document.getElementById(`label-q${qNum}-${userLetter}`);
      
      if (userLetter === correctLetter) {
        // Correct!
        score++;
        userLabel.classList.add('correct');
      } else {
        // Incorrect!
        userLabel.classList.add('incorrect');
        if (correctLabel) {
          // Also show the correct answer
          correctLabel.classList.add('correct');
        }
      }
    } else {
      // No answer given
      if (correctLabel) {
        // Show the correct answer
        correctLabel.classList.add('correct');
      }
    }
  }

  // Display the final score
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = `Your Score: ${score} / ${totalQuestions}`;
  resultsDiv.style.display = 'block';
  
  // Scroll to the top to see the score
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
</script>
""")
        
        f_out.write("</body>\n</html>\n")

    print(f"--- SUCCESS ---")
    print(f"File '{html_file}' has been created with grading logic.")
    print(f"You can open it in your browser!")
    print(f"---------------")


if __name__ == "__main__":
    create_html_quiz(MARKDOWN_FILE, HTML_FILE)