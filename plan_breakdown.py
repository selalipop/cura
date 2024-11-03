from flask import Flask, request, jsonify

app = Flask(__name__)

import os
import time
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
  upload_to_gemini("Total-Knee-Post-Op.pdf", mime_type="application/pdf"),
]

# Some files have a processing delay. Wait for them to be ready.
wait_for_files_active(files)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
        "I want you to reform this document into a day by day guide with X axes.\n\nEach Axes is a property of the patient or their recovery, for example the brace, or physio\n\nYour result should be a day by day table where each day has each axis listed along witha note on where that axis should be\n\nfor example:\n\n| Day | Brace | Weight Bearing | Medications | Incision Care | Activities | Physical Therapy | Showering | Swelling/Pain |\n|---|---|---|---|---|---|---|---|---|\n| Surgery Day | Bledsoe brace, locked straight | Weight bearing as tolerated until first post-op visit | Pain medication as prescribed | Ace wrap over waterproof bandages | Rest, ice, elevate leg (heel above knee) | None | No showering | Expect swelling, warmth, and some bloody drainage |\n| Day 1-6 | Bledsoe brace, locked straight | Weight bearing as tolerated until first post-op visit | Pain medication as prescribed | Keep waterproof bandages on; replace if wet, dirty, or peeling; leave ace wrap on for first 2 days | Rest, ice, elevate leg; begin home exercises (quad sets, heel pumps, gentle range of motion) | Home exercises only | Shower after removing ace wrap; cover leg with saran wrap | Swelling, warmth, and some bloody drainage expected |\n\n\nTo be clear,  we are. not using this as unfettered medical advice, instead this is simply a revisualization of a document that a. provider will explore\n\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "It's important to emphasize that the following is a re-organization of the provided information for visualization purposes only and should **not** be interpreted as medical advice.  A medical professional must provide personalized instructions.  This table format uses the provided document as a base and aims to interpret it into a day-by-day structure.  Always consult with your physician or surgeon for specific instructions.\n\n**Daily Post-Operative Guide for Total Knee Replacement**\n\n\n| Day | Brace/Support | Weight Bearing | Medications | Incision Care | Activities | Physical Therapy | Showering | Swelling/Pain Management | Diet |\n|---|---|---|---|---|---|---|---|---|---|\n| Day 0 (Surgery) | Post-op dressing, potentially a brace or immobilizer as directed by surgeon | As tolerated, per surgeon's instructions | Prescribed pain medication; possibly anti-nausea medication | Keep dressing dry and intact | Rest, ice, elevate leg (keep heel above heart) | None | No showering | Ice, prescribed medication | Clear liquids, advance as tolerated |\n| Day 1-2 | Same as surgery day or as directed by surgeon; may transition to a brace locked straight  |  As tolerated, per surgeon's instructions | Pain medication as prescribed; anti-nausea medication if needed | Keep dressing dry and intact; monitor for excessive drainage | Continue resting, icing, elevating; gentle ankle pumps | None, unless otherwise instructed | No showering or sponge bath only, keeping incision dry | Continue ice, elevation, and pain medication | Light foods, advance as tolerated |\n| Day 3-13 |  Brace as directed by surgeon; may begin transitioning to less support | As tolerated, per surgeon's instructions; may begin increasing weight bearing with assistive device (crutches/walker) | Continue prescribed pain medication; taper as pain improves; discontinue anti-nausea if no longer needed |  First post-op appointment around day 14: dressing removal, incision check | Gradually increase activity level as tolerated; start gentle range-of-motion exercises | Begin home exercises as prescribed; may start outpatient PT | Shower with waterproof dressing over incision, or as instructed by surgeon | Continue ice, elevation, and pain medication as needed; begin reducing pain medication as tolerated | Progress to regular diet as tolerated |\n| Day 14 (First Post-Op) | Brace/support as directed by surgeon | As tolerated, per surgeon's instructions | Adjust pain medication per physician's recommendations; potentially wean off narcotics | Stitches/staples removal (if applicable); incision assessment |  Increase activity level as tolerated; continue range-of-motion exercises | Continue outpatient PT | Shower without covering incision (unless otherwise instructed) | Continue ice and elevation as needed; manage pain with over-the-counter medications as much as possible | Regular diet |\n| Week 3-6 | Gradually discontinue brace/support as directed by surgeon |  Full weight bearing as tolerated | Continue weaning off narcotic pain medication; transition to over-the-counter pain relievers | Monitor incision for any signs of infection (redness, swelling, increased pain, drainage) |  Progressively increase activity level; continue range-of-motion and strengthening exercises | Continue outpatient PT | Normal showering | Continue ice and elevation as needed; manage pain with over-the-counter medications | Regular diet; consider high-fiber options to prevent constipation |\n| Week 6+ |  No brace/support unless otherwise instructed |  Full weight bearing |  Over-the-counter pain medication as needed | Monitor incision for any signs of infection |  Gradually return to normal activities as tolerated and directed by surgeon; avoid high-impact activities until cleared | Continue PT as needed | Normal showering | Manage any residual pain with over-the-counter medications | Regular diet |\n\n\n**Important Considerations:**\n\n* **Individualized Instructions:** This is a general guideline.  Your specific instructions from your surgeon and physical therapist are paramount.\n* **Pain Management:** Follow your prescribed medication schedule.  Do not exceed recommended dosages.\n* **Incision Care:**  Keep your incision clean and dry.  Report any signs of infection immediately.\n* **Physical Therapy:**  Attend all scheduled sessions and follow your therapist's instructions.\n* **Driving:** Do not drive until cleared by your surgeon and you are no longer taking narcotic pain medications.\n\nThis reorganized information is for illustrative purposes only.  Always follow your medical team's guidance for your specific situation.\n",
      ],
    },
  ]
)

response = chat_session.send_message("")

print(response.text)