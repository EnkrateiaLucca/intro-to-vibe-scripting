# One-Shot Scripting with UV and AI

## Introduction

One-shot scripting is the art of creating small, focused Python scripts that solve specific problems quickly and efficiently. By combining UV's powerful script management capabilities with AI assistance, you can create automation solutions without writing code from scratch.

This tutorial shows you how to build a system where you describe what you need, and AI helps you create production-ready Python scripts that run immediately with all dependencies handled automatically.

## What is One-Shot Scripting?

One-shot scripts are small Python programs designed to:
- Solve a specific problem immediately
- Run once or occasionally, not as long-running services
- Handle their own dependencies automatically
- Be easily shareable and reproducible
- Require minimal setup

Examples of one-shot scripts:
- Download and process data from an API
- Convert files between formats
- Send automated emails with reports
- Scrape specific information from websites
- Generate reports from CSV files
- Resize images in bulk
- Clean up file systems

## Why UV + AI is Perfect for One-Shot Scripts

### UV Advantages
- **Zero virtual environment setup** - UV handles dependencies automatically
- **Fast execution** - Dependencies are cached and resolved quickly
- **Portable scripts** - Dependencies are declared in the script itself
- **No pip install needed** - Everything is self-contained

### AI Advantages
- **Natural language to code** - Describe what you need, get working code
- **Dependency knowledge** - AI knows which packages to use
- **Error handling** - AI can add robust error handling
- **Best practices** - AI applies good coding patterns automatically

## Setting Up Your One-Shot Scripting System

### Prerequisites

1. **Install UV** (if you haven't already):
   ```bash
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Choose your AI tool** - Any of these work great:
   - ChatGPT
   - Claude
   - GitHub Copilot
   - Local models via Ollama

### The UV Script Format

UV scripts use special comments to declare dependencies:

```python
#!/usr/bin/env python3
"""
Script description here
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
#     "pandas",
# ]
# ///

import requests
import pandas as pd
from bs4 import BeautifulSoup

# Your script code here
```

The magic happens in the `# /// script` block - UV reads this and automatically installs the required packages when you run the script.

## The One-Shot Scripting Workflow

### Step 1: Describe Your Need
Instead of thinking in code, think in outcomes. For example:

❌ **Don't think:** "I need to import requests, parse JSON, iterate through data..."

✅ **Do think:** "I want to download all GitHub repositories for a user and save the names and descriptions to a CSV file."

### Step 2: Prompt the AI
Use this template for consistent results:

```
Create a UV-compatible Python script that [YOUR GOAL].

Requirements:
- Use UV script format with dependencies declared in comments
- Include proper error handling
- Add helpful print statements for progress
- Make it executable with: uv run script_name.py
- [Any specific requirements]

The script should [DETAILED DESCRIPTION OF WHAT IT SHOULD DO].
```

### Step 3: Test and Iterate
Run the script with UV and refine as needed:

```bash
uv run your_script.py
```

If it doesn't work perfectly, copy the error back to AI and ask for fixes.

## Example One-Shot Scripts

### Example 1: GitHub Repository Analyzer

**Prompt to AI:**
"Create a UV-compatible Python script that fetches all public repositories for a GitHub username and saves them to a CSV with name, description, language, and star count."

**Generated Script:**
```python
#!/usr/bin/env python3
"""
GitHub Repository Analyzer
Fetches all public repos for a user and saves to CSV
Usage: uv run github_analyzer.py username
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31.0",
#     "pandas>=2.0.0",
# ]
# ///

import sys
import requests
import pandas as pd
from typing import List, Dict

def fetch_repositories(username: str) -> List[Dict]:
    """Fetch all public repositories for a GitHub user"""
    repos = []
    page = 1
    
    print(f"📡 Fetching repositories for {username}...")
    
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {"per_page": 100, "page": page, "sort": "updated"}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
            return []
        
        page_repos = response.json()
        if not page_repos:
            break
            
        repos.extend(page_repos)
        page += 1
        print(f"   Found {len(page_repos)} repositories on page {page-1}")
    
    return repos

def process_repositories(repos: List[Dict]) -> pd.DataFrame:
    """Process repository data into a clean DataFrame"""
    processed = []
    
    for repo in repos:
        processed.append({
            "name": repo["name"],
            "description": repo["description"] or "No description",
            "language": repo["language"] or "Unknown",
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "created": repo["created_at"][:10],  # Just the date
            "updated": repo["updated_at"][:10],
            "url": repo["html_url"]
        })
    
    return pd.DataFrame(processed)

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run github_analyzer.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    
    # Fetch repositories
    repos = fetch_repositories(username)
    if not repos:
        return
    
    # Process data
    df = process_repositories(repos)
    
    # Save to CSV
    filename = f"{username}_repositories.csv"
    df.to_csv(filename, index=False)
    
    # Show summary
    print(f"\n✅ Analysis complete!")
    print(f"📊 Total repositories: {len(df)}")
    print(f"⭐ Total stars: {df['stars'].sum()}")
    print(f"🍴 Total forks: {df['forks'].sum()}")
    print(f"💾 Saved to: {filename}")
    
    # Show top repositories
    top_repos = df.nlargest(5, "stars")
    print(f"\n🏆 Top 5 repositories by stars:")
    for _, repo in top_repos.iterrows():
        print(f"   {repo['name']}: {repo['stars']} ⭐")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
uv run github_analyzer.py octocat
```

### Example 2: Image Resizer

**Prompt to AI:**
"Create a UV-compatible Python script that resizes all images in a directory to a specified width while maintaining aspect ratio."

**Generated Script:**
```python
#!/usr/bin/env python3
"""
Bulk Image Resizer
Resizes all images in a directory to specified width
Usage: uv run resize_images.py <directory> <width>
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pillow>=10.0.0",
# ]
# ///

import sys
import os
from pathlib import Path
from PIL import Image

def resize_image(input_path: Path, output_path: Path, target_width: int):
    """Resize a single image maintaining aspect ratio"""
    try:
        with Image.open(input_path) as img:
            # Calculate new height maintaining aspect ratio
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            
            # Resize image
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            resized_img.save(output_path, optimize=True, quality=85)
            
        return True
    except Exception as e:
        print(f"❌ Error processing {input_path.name}: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: uv run resize_images.py <directory> <width>")
        print("Example: uv run resize_images.py ./photos 800")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    try:
        target_width = int(sys.argv[2])
    except ValueError:
        print("❌ Width must be a number")
        sys.exit(1)
    
    if not directory.exists():
        print(f"❌ Directory {directory} does not exist")
        sys.exit(1)
    
    # Create output directory
    output_dir = directory / "resized"
    output_dir.mkdir(exist_ok=True)
    
    # Supported image formats
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
    
    # Find all images
    images = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not images:
        print(f"❌ No images found in {directory}")
        return
    
    print(f"🖼️  Found {len(images)} images to resize")
    print(f"📐 Target width: {target_width}px")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Process images
    successful = 0
    for image_path in images:
        output_path = output_dir / f"resized_{image_path.name}"
        print(f"Processing {image_path.name}...", end=" ")
        
        if resize_image(image_path, output_path, target_width):
            print("✅")
            successful += 1
        else:
            print("❌")
    
    print(f"\n✅ Completed! Successfully resized {successful}/{len(images)} images")

if __name__ == "__main__":
    main()
```

### Example 3: CSV Data Cleaner

**Prompt to AI:**
"Create a UV-compatible script that cleans a CSV file by removing duplicates, handling missing values, and standardizing text columns."

**Generated Script:**
```python
#!/usr/bin/env python3
"""
CSV Data Cleaner
Cleans CSV files by removing duplicates and handling missing data
Usage: uv run clean_csv.py <input_file> [output_file]
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0.0",
# ]
# ///

import sys
import pandas as pd
from pathlib import Path

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame with common data cleaning operations"""
    print("🧹 Starting data cleaning...")
    
    original_rows = len(df)
    print(f"📊 Original data: {original_rows} rows, {len(df.columns)} columns")
    
    # 1. Remove completely empty rows
    df = df.dropna(how='all')
    print(f"🗑️  Removed {original_rows - len(df)} completely empty rows")
    
    # 2. Remove duplicate rows
    duplicates = df.duplicated().sum()
    df = df.drop_duplicates()
    print(f"🔄 Removed {duplicates} duplicate rows")
    
    # 3. Clean text columns
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        # Strip whitespace
        df[col] = df[col].astype(str).str.strip()
        # Replace 'nan', 'null', empty strings with NaN
        df[col] = df[col].replace(['nan', 'null', 'NULL', 'None', ''], pd.NA)
    
    print(f"🧽 Cleaned {len(text_columns)} text columns")
    
    # 4. Show missing data summary
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print("\n📋 Missing data summary:")
        for col, count in missing_data[missing_data > 0].items():
            percentage = (count / len(df)) * 100
            print(f"   {col}: {count} missing ({percentage:.1f}%)")
    
    print(f"\n✅ Cleaning complete: {len(df)} rows remaining")
    return df

def analyze_data(df: pd.DataFrame):
    """Provide basic analysis of the cleaned data"""
    print("\n📈 Data Analysis:")
    print(f"📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Data types
    print(f"🔢 Numeric columns: {len(df.select_dtypes(include=['number']).columns)}")
    print(f"📝 Text columns: {len(df.select_dtypes(include=['object']).columns)}")
    print(f"📅 Date columns: {len(df.select_dtypes(include=['datetime']).columns)}")
    
    # Memory usage
    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f"💾 Memory usage: {memory_mb:.2f} MB")

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run clean_csv.py <input_file> [output_file]")
        print("Example: uv run clean_csv.py data.csv cleaned_data.csv")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"❌ Input file {input_file} does not exist")
        sys.exit(1)
    
    # Determine output file
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.stem + "_cleaned.csv"
    
    try:
        # Load CSV
        print(f"📂 Loading {input_file}...")
        df = pd.read_csv(input_file)
        
        # Clean data
        cleaned_df = clean_dataframe(df)
        
        # Analyze data
        analyze_data(cleaned_df)
        
        # Save cleaned data
        print(f"\n💾 Saving to {output_file}...")
        cleaned_df.to_csv(output_file, index=False)
        
        print(f"✅ Successfully cleaned and saved data to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Advanced One-Shot Patterns

### 1. Configuration via Command Line Arguments

Make scripts flexible with `argparse`:

```python
# /// script
# dependencies = ["argparse"]
# ///

import argparse

def main():
    parser = argparse.ArgumentParser(description="My one-shot script")
    parser.add_argument("input", help="Input file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    # Use args.input, args.output, args.verbose
```

### 2. Environment-Based Configuration

Handle secrets and config via environment variables:

```python
import os

# Get API keys from environment
api_key = os.getenv("API_KEY")
if not api_key:
    print("❌ Please set API_KEY environment variable")
    sys.exit(1)
```

### 3. Progress Tracking for Long Operations

Show progress for time-consuming tasks:

```python
# /// script
# dependencies = ["tqdm"]
# ///

from tqdm import tqdm
import time

items = range(100)
for item in tqdm(items, desc="Processing"):
    # Do work
    time.sleep(0.1)
```

### 4. Robust Error Handling

Add proper error handling and logging:

```python
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Your main logic
    pass
except Exception as e:
    logger.error(f"Script failed: {e}")
    sys.exit(1)
```

## Best Practices for AI-Assisted One-Shot Scripts

### 1. Be Specific in Your Prompts

❌ **Vague:** "Create a script to process files"

✅ **Specific:** "Create a UV script that converts all PNG images in a directory to JPEG format, reducing quality to 80% and adding a watermark"

### 2. Ask for Production-Ready Features

Always request:
- Error handling
- Progress indicators
- Help messages
- Input validation
- Meaningful output

### 3. Iterate and Improve

Don't expect perfection on the first try:
1. Run the script
2. Note what doesn't work or could be better
3. Ask AI to fix or enhance specific parts
4. Repeat until satisfied

### 4. Request Multiple Approaches

For complex tasks, ask: "Show me two different approaches to solve this problem" - then pick the best parts from each.

### 5. Ask for Documentation

Always request: "Add docstrings and comments explaining how this works"

## Common One-Shot Script Patterns

### 1. Data Processing Pipeline
**Pattern:** `Input → Load Data → Transform → Validate → Output → Report`

**CSV/Excel Processing:**
- Clean messy CSV files (remove duplicates, fix encoding, standardize formats)
- Merge multiple spreadsheets into a single dataset
- Convert Excel files to CSV with specific sheet selection
- Split large CSV files into smaller chunks
- Validate data against business rules (email formats, date ranges, etc.)
- Generate data quality reports with missing values and outliers

**Database Operations:**
- Extract data from database to CSV/JSON for analysis
- Sync data between different databases
- Clean and migrate legacy data to new schema
- Generate database backup reports
- Create sample datasets from production data

**Log File Analysis:**
- Parse web server logs to extract visitor statistics
- Analyze application logs for error patterns
- Generate security reports from firewall logs
- Process system logs to identify performance bottlenecks
- Extract specific events from large log files

**Data Format Conversion:**
- Convert JSON to CSV for spreadsheet analysis
- Transform XML data to JSON for web applications
- Convert CSV to SQL INSERT statements
- Transform API responses to tabular format
- Convert between different date/time formats across datasets

### 2. API Integration
**Pattern:** `Configure → Authenticate → Fetch → Process → Store → Notify`

**Social Media Automation:**
- Post content to multiple social platforms simultaneously
- Fetch trending hashtags for content planning
- Monitor mentions and sentiment across platforms
- Download all posts from a specific account
- Generate social media analytics reports

**Cloud Service Management:**
- Backup files to multiple cloud storage providers
- Sync files between different cloud services
- Monitor cloud service usage and costs
- Automatically organize photos by date/location
- Download all files from a cloud service for local backup

**Financial Data:**
- Fetch daily stock prices and generate alerts
- Monitor cryptocurrency prices and send notifications
- Download bank transaction data for expense analysis
- Track investment portfolio performance
- Generate tax-ready financial reports

**Weather and Environmental:**
- Daily weather reports sent to email/Slack
- Monitor air quality and send health alerts
- Track seasonal weather patterns over time
- Generate weather-based recommendations
- Monitor severe weather alerts for specific locations

**Communication Automation:**
- Send scheduled messages to Slack/Discord channels
- Monitor email inbox and categorize messages
- Send SMS alerts for important events
- Automatically respond to common support requests
- Generate and send weekly team status reports

**E-commerce and Business:**
- Monitor product prices across different websites
- Track inventory levels and send restock alerts
- Download order data for accounting systems
- Monitor competitor pricing and features
- Generate sales performance reports

### 3. File Operations
**Pattern:** `Scan Directory → Filter Files → Process Each → Handle Errors → Summary`

**Media File Management:**
- Bulk resize/compress images for web use
- Convert videos to different formats/resolutions
- Organize photos by date taken or location
- Extract metadata from media files
- Generate thumbnails for video files
- Remove duplicate images based on content similarity

**Document Processing:**
- Convert Word documents to PDF in bulk
- Extract text from PDF files for analysis
- Merge multiple PDFs into single documents
- Generate document inventories with metadata
- OCR scanned documents to searchable text
- Standardize document naming conventions

**Code and Development:**
- Format code files according to style guidelines
- Count lines of code across project directories
- Find and replace patterns across multiple files
- Generate project documentation from code comments
- Archive old project files with compression
- Scan for security vulnerabilities in dependencies

**System Maintenance:**
- Clean temporary files and clear caches
- Organize downloads folder by file type/date
- Find and remove large unused files
- Backup specific file types to external storage
- Monitor disk space usage across directories
- Generate file system health reports

**Backup and Archiving:**
- Create incremental backups of important directories
- Compress and archive old project files
- Sync important files to multiple locations
- Verify backup integrity and completeness
- Restore files from backup based on date ranges
- Generate backup status reports

### 4. Report Generation
**Pattern:** `Gather Data → Calculate Metrics → Format Output → Save/Send → Log Results`

**Business Analytics:**
- Daily sales performance dashboards
- Customer behavior analysis from web analytics
- Employee productivity reports from time tracking
- Inventory turnover and stock level reports
- Marketing campaign ROI analysis
- Monthly financial summaries with charts

**System Monitoring:**
- Server performance and uptime reports
- Website speed and availability monitoring
- Database performance metrics
- Security incident summaries
- Resource usage trends over time
- Application error rate analysis

**Project Management:**
- Sprint progress and velocity reports
- Task completion rates by team member
- Project timeline and milestone tracking
- Budget vs. actual spending analysis
- Risk assessment and mitigation reports
- Team workload distribution analysis

**Academic and Research:**
- Survey data analysis with statistical summaries
- Literature review compilation from research databases
- Experiment result processing and visualization
- Student grade analysis and distribution reports
- Research citation tracking and impact metrics
- Academic calendar and deadline reminders

### 5. Content and Communication
**Pattern:** `Source Content → Process → Format → Distribute → Track`

**Content Creation:**
- Generate blog post ideas from trending topics
- Create social media content calendars
- Convert long-form content to multiple formats
- Generate email newsletters from curated content
- Create presentation slides from outline text
- Automate video thumbnail generation

**Email Automation:**
- Send personalized bulk emails with tracking
- Process email subscription/unsubscription requests
- Generate email campaign performance reports
- Archive important emails to specific folders
- Forward emails based on content filtering rules
- Create email digest summaries

**Documentation:**
- Generate API documentation from code
- Create user manuals from feature specifications
- Update README files with latest project info
- Generate change logs from commit messages
- Create team onboarding guides
- Maintain knowledge base articles

### 6. Web Scraping and Monitoring
**Pattern:** `Target Sites → Scrape Data → Parse Content → Store → Alert`

**Price Monitoring:**
- Track product prices across e-commerce sites
- Monitor real estate listings for specific criteria
- Watch for stock availability notifications
- Compare service pricing across providers
- Track historical price trends
- Send alerts when price thresholds are met

**Content Monitoring:**
- Monitor news sites for specific keywords
- Track job postings matching criteria
- Watch for new content from favorite blogs/sites
- Monitor competitor website changes
- Track social media mentions of brands/topics
- Generate content aggregation newsletters

**Data Collection:**
- Gather contact information from business directories
- Collect event listings from multiple sources
- Download public datasets for research
- Monitor government data releases
- Track scientific publication updates
- Compile industry report summaries

### 7. System Administration
**Pattern:** `Check Status → Identify Issues → Take Action → Log Results → Report`

**Security and Maintenance:**
- Scan systems for security vulnerabilities
- Monitor failed login attempts and suspicious activity
- Update software packages across multiple systems
- Generate security compliance reports
- Monitor SSL certificate expiration dates
- Perform automated security audits

**Performance Optimization:**
- Analyze system performance bottlenecks
- Clean up disk space and optimize storage
- Monitor network usage and bandwidth
- Optimize database performance automatically
- Generate system health check reports
- Monitor and restart failed services

**User Management:**
- Onboard new users with account creation
- Offboard users and disable access
- Generate user access reports
- Monitor user activity for compliance
- Sync user data between systems
- Generate password expiration reminders

### 8. Personal Productivity
**Pattern:** `Collect Input → Process → Organize → Schedule → Remind`

**Task and Time Management:**
- Sync tasks between different productivity apps
- Generate weekly/monthly productivity reports
- Automatically schedule recurring tasks
- Track time spent on different activities
- Generate habit tracking visualizations
- Create personalized daily agenda emails

**Health and Fitness:**
- Track exercise data from multiple sources
- Generate nutrition reports from food logs
- Monitor sleep patterns and generate insights
- Create workout plans based on preferences
- Track medication schedules and reminders
- Generate health trend reports

**Finance and Budgeting:**
- Categorize expenses from bank transactions
- Generate monthly budget vs. actual reports
- Track subscription services and their costs
- Monitor investment portfolio performance
- Generate tax preparation summaries
- Create bill payment reminders

### 9. Learning and Education
**Pattern:** `Gather Resources → Organize → Process → Practice → Assess`

**Study Aids:**
- Generate flashcards from study materials
- Create quiz questions from textbook content
- Organize research papers by topic
- Generate study schedules from curriculum
- Track learning progress and goals
- Create personalized study reminders

**Skill Development:**
- Curate learning resources for specific skills
- Track online course progress across platforms
- Generate certificates and completion reports
- Create practice exercises from tutorials
- Monitor skill development metrics
- Generate learning path recommendations

### 10. Creative and Design
**Pattern:** `Gather Inspiration → Generate Ideas → Create Assets → Organize → Share`

**Asset Management:**
- Organize design assets by project/client
- Generate design system documentation
- Create brand guideline compliance reports
- Batch process design file conversions
- Generate creative brief templates
- Archive completed project assets

**Content Generation:**
- Generate color palettes from images
- Create design mockups from wireframes
- Generate placeholder content for designs
- Create style guide documentation
- Generate brand asset variations
- Create design presentation materials

## Prompt Templates for Each Pattern

### Data Processing Prompt:
```
Create a UV script that processes [DATA_TYPE] files by:
1. Loading data from [SOURCE]
2. Cleaning/transforming: [SPECIFIC_OPERATIONS]
3. Validating: [VALIDATION_RULES]
4. Outputting to: [FORMAT/DESTINATION]
5. Generating a summary report

Include progress indicators and error handling.
```

### API Integration Prompt:
```
Create a UV script that integrates with [API_NAME] to:
1. Authenticate using [AUTH_METHOD]
2. Fetch [DATA_TYPE] with these parameters: [PARAMS]
3. Process the data by [PROCESSING_STEPS]
4. Store results in [FORMAT/LOCATION]
5. Send notification to [NOTIFICATION_METHOD]

Handle rate limits and API errors gracefully.
```

### File Operations Prompt:
```
Create a UV script that processes files by:
1. Scanning [DIRECTORY/PATTERN]
2. Filtering files matching [CRITERIA]
3. Performing [OPERATION] on each file
4. Handling errors and logging results
5. Generating a summary of actions taken

Include dry-run mode and backup options.
```

### Report Generation Prompt:
```
Create a UV script that generates a [REPORT_TYPE] by:
1. Gathering data from [SOURCES]
2. Calculating these metrics: [METRICS_LIST]
3. Creating visualizations for [CHART_TYPES]
4. Formatting as [OUTPUT_FORMAT]
5. Distributing via [DELIVERY_METHOD]

Include interactive elements and export options.
```

## Troubleshooting Common Issues

### Script Won't Run
```bash
# Check UV installation
uv --version

# Run with verbose output
uv run --verbose script.py

# Check script syntax
python -m py_compile script.py
```

### Dependency Issues
```bash
# Clear UV cache
uv cache clean

# Check exact dependencies
uv pip list

# Try running without UV first
python script.py
```

### Permission Errors
```bash
# Make script executable
chmod +x script.py

# Check file permissions
ls -la script.py
```

## Building Your One-Shot Script Library

### Organize by Category
```
scripts/
├── data-processing/
├── file-operations/
├── api-tools/
├── image-processing/
├── text-processing/
└── system-admin/
```

### Template Script
Create a template for consistent structure:

```python
#!/usr/bin/env python3
"""
[SCRIPT NAME]
[DESCRIPTION]
Usage: uv run [script_name].py [arguments]
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     # Add your dependencies here
# ]
# ///

import sys
from pathlib import Path

def main():
    """Main script logic"""
    if len(sys.argv) < 2:
        print("Usage: uv run script.py <argument>")
        sys.exit(1)
    
    # Your code here
    print("✅ Script completed successfully!")

if __name__ == "__main__":
    main()
```

### Version Control Your Scripts
```bash
# Initialize git repository for your scripts
cd ~/scripts
git init
git add .
git commit -m "Initial script collection"
```

## Conclusion

One-shot scripting with UV and AI transforms how you approach automation:

1. **Think in outcomes, not code** - Describe what you need
2. **Let AI handle the implementation** - Focus on the problem, not the syntax
3. **UV handles the environment** - No setup friction
4. **Iterate quickly** - Run, refine, repeat

This approach makes Python automation accessible to everyone, regardless of coding experience. You can solve real problems immediately without getting bogged down in setup or syntax.

Start with simple scripts and gradually build more complex ones. Soon you'll have a library of custom tools that solve your specific needs, all created through natural language conversations with AI.

The combination of UV's simplicity and AI's code generation capabilities represents the future of practical programming - where ideas become working code in minutes, not hours.

## Next Steps

1. Install UV if you haven't already
2. Try creating your first one-shot script with AI
3. Build a script that solves a real problem you have
4. Share your scripts with others
5. Start building your personal automation library

Happy scripting! 🚀
