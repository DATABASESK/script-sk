import datetime
import requests
import random
# FIX: Change import to the full module path to avoid conflicts
import google.generativeai as genai
import tweepy
import random
import os

# --- Load Secrets from Environment ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN_LI = os.getenv("ACCESS_TOKEN_LI")
PERSON_URN = os.getenv("PERSON_URN")
ACCESS_TOKEN_IG = os.getenv("ACCESS_TOKEN_IG")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")   # renamed to avoid collision
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# --- GitHub Repo Info (these are public, so keep them here) ---
REPO_OWNER = "DATABASESK"
REPO_NAME = "kishore-personal-"
BRANCH = "main"
CONTENT_BASE_PATH = "content"


# --- NOTE ---
# In a real environment, you must ensure all the required variables (like those in the block above)
# are defined and hold actual values before this script runs.
# ==============================================================================
# 2. DYNAMIC CONTENT SETUP & CONSTANTS
# ==============================================================================

# Get today's date (e.g., "2025-09-27")
TODAY_FOLDER = datetime.date.today().strftime("%Y-%m-%d")

# Base URL for raw content on GitHub
GITHUB_RAW_BASE_URL = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/"
    f"{CONTENT_BASE_PATH}/{TODAY_FOLDER}"
)

# Dynamic URLs for today's content
IMAGE_URL = f"{GITHUB_RAW_BASE_URL}/image.png"
LINKEDIN_CAPTION_URL = f"{GITHUB_RAW_BASE_URL}/caption_linkedin.txt"
INSTAGRAM_CAPTION_URL = f"{GITHUB_RAW_BASE_URL}/caption_instagram.txt"

# X Platform maximum character limit
MAX_TWEET_LENGTH = 280

# ==============================================================================
# 3. UTILITY FUNCTIONS (Content Fetching and Generation)
# ==============================================================================

def generate_gemini_article_text():
    """Generates a long, detailed LinkedIn article with clean formatting (no asterisks)."""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("🛑 GEMINI_API_KEY is not set in the CONFIGURATION section. Aborting content generation.")
        return None

    try:
        # Client initialization remains the same: genai.Client
        client = genai.Client(api_key=GEMINI_API_KEY)

        # FINAL OPTIMIZED PROMPT: Requests clear structure and explicitly forbids asterisk formatting.
        system_instruction = (
            "You are a savvy digital marketing expert. Generate a **long, detailed, and highly valuable** "
            "LinkedIn article structured as **'Real-World Digital Marketing Tips and Tricks'**. "
            "Use a headline in **ALL CAPS** for impact, and break down the tips using **numbered headings** followed by double line breaks. "
            "**DO NOT use asterisk symbols (*)** for formatting or bolding, use line breaks and numbering for clarity. "
            "The content should maximize information density. "
            "The **ENTIRE POST MUST NOT EXCEED 2,500 CHARACTERS** (including all headings and signatures). "
            "Crucially, the content must naturally include the name 'KISHORE S' and the handle '@growwithkishore' "
            "at least once, which is vital for search engine visibility. End the post with relevant hashtags."
        )

        print("🤖 Generating LONG, Cleanly Formatted Article Content with Gemini API...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Generate today's real-world digital marketing tips and tricks article.",
            config={
                "system_instruction": system_instruction,
            }
        )
        
        return response.text.strip()

    except Exception as e:
        print(f"🛑 Gemini API Error: Could not generate content. Error: {e}")
        return None

def generate_tweet_content(api_key: str):
    """
    Uses the Gemini API to generate a tweet about digital marketing tools,
    adhering to the character limit and including required mentions.
    """
    print("\n🤖 Generating X (Twitter) Content with Gemini API...")
    if api_key == "YOUR_ACTUAL_GEMINI_API_KEY" or not api_key: # Use GEMINI_API_KEY from global scope
        print("❌ ERROR: Gemini API key is missing or is a placeholder. Cannot generate X content.")
        return None

    try:
        # Initialize the Gemini Client by passing the API key directly
        client = genai.Client(api_key=api_key)

        # System Instruction for the model
        system_instruction = (
            f"You are a helpful and engaging social media expert focused on digital marketing. "
            f"Generate a single, high-impact tweet about a real-world digital marketing tool or new technology. "
            f"The content MUST NOT exceed {MAX_TWEET_LENGTH} characters. "
            f"The tweet MUST include the text 'KISHORE S' and the handle '@growwithkishore'. "
            f"Use 1-2 relevant emojis and 1-2 popular digital marketing hashtags (e.g., #DigitalMarketing, #MarTech). "
            f"DO NOT include any introductory or concluding text, ONLY the tweet content."
        )

        # Topics for variety
        topics = [
            "Practical uses of Generative AI in content creation",
            "The best new MarTech tools for small businesses",
            "Latest privacy-first analytics and measurement technologies",
            "Real-world application of programmatic advertising",
            "New features in social media platform algorithms"
        ]

        prompt_text = f"Generate a tweet on the topic: {random.choice(topics)}"

        # Generate content
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.8  # Creativity level
            }
        )

        tweet_content = response.text.strip()
        
        # Simple cleanup and final check
        required_suffix = f" | KISHORE S @growwithkishore"
        # The model is strictly instructed, but we add a check for robustness.
        if "KISHORE S" not in tweet_content or "@growwithkishore" not in tweet_content:
             # If required elements are missing, append them and potentially truncate the start
             # This simple check is less robust than a full regex search, but catches major omissions
             if len(tweet_content) + len(required_suffix) < MAX_TWEET_LENGTH:
                 tweet_content = tweet_content.strip() + required_suffix
             else:
                 # Truncate to fit
                 truncate_len = MAX_TWEET_LENGTH - len(required_suffix) - 3 # -3 for "..."
                 tweet_content = tweet_content[:truncate_len].strip() + "..." + required_suffix.split(' | ')[1]
        
        # Final check and potential truncation
        if len(tweet_content) > MAX_TWEET_LENGTH:
             # Should be rare given the prompt, but safety first
             tweet_content = tweet_content[:MAX_TWEET_LENGTH - 3].strip() + "..."
             print(f"⚠️ Warning: Final tweet truncated to {len(tweet_content)} characters.")


        print(f"✅ Generated Tweet (Length: {len(tweet_content)}):\n---\n{tweet_content}\n---")
        return tweet_content

    except Exception as e:
        print(f"❌ An error occurred during Gemini API call for X: {e}")
        return None


def fetch_caption(caption_url):
    """Fetches the caption text from the GitHub raw URL."""
    try:
        response = requests.get(caption_url)
        response.raise_for_status() 
        return response.text.strip()
    except requests.exceptions.HTTPError as e:
        print(f"🛑 Error: Could not find content at {caption_url}. (HTTP Status {e.response.status_code})")
        print("    Ensure the folder and file names are correct for the current date.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🛑 Network Error fetching caption from {caption_url}: {e}")
        return None

# ==============================================================================
# 4. LINKEDIN POSTING FUNCTIONS (TWO SEPARATE POSTS)
# ==============================================================================

def post_media_update_to_linkedin():
    """Posts an Image and Caption using content fetched from GitHub."""
    print("\n--- Starting LinkedIn Image/Caption Post (via GitHub) ---")
    
    if not ACCESS_TOKEN_LI or not PERSON_URN:
        print("🛑 LinkedIn credentials missing. Aborting media post.")
        return

    # Fetches the caption from GitHub for the image post
    POST_TEXT = fetch_caption(LINKEDIN_CAPTION_URL)
    if not POST_TEXT:
        print("🛑 LinkedIn caption fetch failed. Aborting media post.")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN_LI}",
        "Content-Type": "application/json"
    }

    try:
        # === STEPS 1 & 2: Register and Upload Image ===
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        register_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": PERSON_URN,
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ]
            }
        }
        res = requests.post(register_url, json=register_body, headers=headers)
        res.raise_for_status()
        register_data = res.json()
        upload_url = register_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_urn = register_data['value']['asset']
        print(f"✅ Step 1: Registered upload. Asset URN: {asset_urn}")

        print(f"    Fetching image from: {IMAGE_URL}")
        image_data = requests.get(IMAGE_URL).content
        
        upload_headers = {"Authorization": f"Bearer {ACCESS_TOKEN_LI}", "Content-Type": "application/octet-stream"}
        res = requests.put(upload_url, data=image_data, headers=upload_headers)
        res.raise_for_status()
        print("✅ Step 2: Image uploaded successfully.")

        # === STEP 3: Post text + image ===
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        post_body = {
            "author": PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": POST_TEXT},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {"status": "READY", "media": asset_urn}
                    ]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        res = requests.post(post_url, json=post_body, headers=headers)
        res.raise_for_status()
        print("🎉 Step 3: LinkedIn Image/Caption Post created successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"🛑 LinkedIn Media Post FAILED. Error: {e}")
        if e.response is not None:
             print(f"    Response Status: {e.response.status_code}, Details: {e.response.text[:200]}...")


def post_gemini_article_to_linkedin():
    """Posts a text-only Article generated by the Gemini API."""
    print("\n--- Starting LinkedIn Article Post (via Gemini API) ---")
    
    if not ACCESS_TOKEN_LI or not PERSON_URN:
        print("🛑 LinkedIn credentials missing. Aborting article post.")
        return

    # >>> Gemini Content Generation <<<<
    ARTICLE_TEXT = generate_gemini_article_text()
    if not ARTICLE_TEXT:
        print("🛑 Article content generation failed. Aborting article post.")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN_LI}",
        "Content-Type": "application/json"
    }

    try:
        # Post the text-only article as a general UGC post
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        post_body = {
            "author": PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": ARTICLE_TEXT},
                    "shareMediaCategory": "NONE" # Text-only post
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        res = requests.post(post_url, json=post_body, headers=headers)
        res.raise_for_status()
        print("🎉 LinkedIn Article Post (Gemini content) created successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"🛑 LinkedIn Article Post FAILED. Error: {e}")
        if e.response is not None:
             print(f"    Response Status: {e.response.status_code}, Details: {e.response.text[:200]}...")

# ==============================================================================
# 5. X (Twitter) POSTING FUNCTION
# ==============================================================================

def post_tweet(tweet_text):
    """
    Authenticates with the X API using OAuth 1.0a and posts the provided tweet
    using the modern tweepy Client.
    """
    print("\n--- Starting X (Twitter) Post ---")
    if not tweet_text:
        print("❌ Cannot post. Tweet content is empty.")
        return
    
    # Check for X credentials
    if not all([CONSUMER_KEY, CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
         print("🛑 X API credentials missing. Aborting X post.")
         return

    try:
        # Initialize the Tweepy Client for API v2
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET
        )
        
        # Verify permissions are available for the user (optional but good for debugging)
        try:
             client.get_me()
             print("✅ X API Authentication successful.")
        except Exception as e:
             print(f"❌ X API Authentication failed. Error: {e}")
             return

        # Post the tweet
        response = client.create_tweet(text=tweet_text)
        
        tweet_id = response.data['id']
        # The URL uses 'x.com' for the current platform name
        tweet_url = f"https://x.com/growwithkishore/status/{tweet_id}" 
        
        print(f"🎉 Successfully posted tweet to X account @growwithkishore!")
        print(f"Link: {tweet_url}")

    except tweepy.TweepyException as e:
        print(f"❌ An error occurred during X API interaction (Tweepy Exception): {e}")
    except Exception as e:
        print(f"❌ A general error occurred during X posting: {e}")

# ==============================================================================
# 6. INSTAGRAM POSTING FUNCTION
# ==============================================================================

def post_to_instagram():
    """Handles the 2-step process to post an image and caption to Instagram."""
    print("\n--- Starting Instagram Post ---")
    
    if not ACCESS_TOKEN_IG or not INSTAGRAM_BUSINESS_ID:
        print("🛑 Instagram credentials missing. Aborting Instagram post.")
        return

    CAPTION_TEXT = fetch_caption(INSTAGRAM_CAPTION_URL)
    if not CAPTION_TEXT:
        print("🛑 Instagram caption fetch failed. Aborting post.")
        return

    try:
        # === STEP 1: Create Media Container with Caption ===
        media_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_BUSINESS_ID}/media"
        media_params = {
            "image_url": IMAGE_URL, # GitHub raw link works as a public hosted image URL
            "caption": CAPTION_TEXT,
            "access_token": ACCESS_TOKEN_IG
        }

        print(f"    Creating media container with image URL: {IMAGE_URL}")
        res = requests.post(media_url, data=media_params)
        res.raise_for_status()
        media_container_id = res.json().get("id")

        if not media_container_id:
            print(f"🛑 Error: Container ID not found. Response: {res.json()}")
            return

        print(f"✅ Step 1: Media container created. ID: {media_container_id}")

        # === STEP 2: Publish the Media ===
        publish_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_BUSINESS_ID}/media_publish"
        publish_params = {
            "creation_id": media_container_id,
            "access_token": ACCESS_TOKEN_IG
        }

        print("    Attempting to publish post...")
        res = requests.post(publish_url, data=publish_params)
        res.raise_for_status()
        print("🎉 Step 2: Instagram Post published successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"🛑 Instagram Post FAILED. Error: {e}")
        if e.response is not None:
            print(f"    Response Status: {e.response.status_code}, Details: {e.response.text[:200]}...")


# ==============================================================================
# 7. MAIN EXECUTION (Unified)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 Starting Unified Social Media Automation for: {TODAY_FOLDER}")
    print("=" * 60)
    
    # --- X (Twitter) Post ---
    # 1. Generate the tweet content using Gemini
    final_tweet = generate_tweet_content(GEMINI_API_KEY)
    
    # 2. Post the content to X
    if final_tweet:
        post_tweet(final_tweet)
    else:
        print("⚠️ X Post Skipped: Content generation failed.")

    print("\n" + "=" * 60)

    # --- LinkedIn Posts (Two Separate Posts) ---
    
    # 3. Post the regular image update (uses GitHub for image and caption)
    post_media_update_to_linkedin()
    
    print("\n" + "=" * 60)

    # 4. Post the Gemini-generated Article (text-only)
    post_gemini_article_to_linkedin()
    
    print("\n" + "=" * 60)

    # --- Instagram Post ---
    
    # 5. Post to Instagram
    post_to_instagram()
    
    print("\n" + "=" * 60)
    print("✅ Full Automation Sequence Complete. (Attempted 4 posts across 3 platforms)")
