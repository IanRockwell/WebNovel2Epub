import time
import os
import utils.scraper_manager as scraper_manager
import utils.epub_manager as epub_manager

BAR = "--------------------------------"

def main():

    print(BAR)
    print("WebNovel2Epub - Author: Ian Rockwell")
    print(BAR)

    print("Supported sites:")
    for site in scraper_manager.SCRAPERS:
        print(f"- {site}")

    print(BAR)

    while True:
        url = input("Enter the URL of the webnovel: ")
        try:
            novel_info = scraper_manager.scrape_series_info(url)
            break

        except ValueError as e:
            print("Error: Could not find the novel. Please check the URL and try again.")

    print(BAR)
    print("\nNovel Information:")
    print(f"Title: {novel_info['title']}")
    print(f"Author: {novel_info['author']}")
    print(f"Genre: {novel_info['genre']}")
    print(BAR)

    while True:
        first_chapter = int(input("Enter the starting chapter number: "))
        last_chapter = int(input("Enter the ending chapter number: "))
        try:
            scraper_manager.scrape_chapter(url, first_chapter)
            scraper_manager.scrape_chapter(url, last_chapter)
            break
        except ValueError as e:
            print(f"Error: Could not find chapter(s). Please verify chapters {first_chapter} through {last_chapter} exist.")

    print("\nStarting chapter download...")
    all_chapters = []
    
    for chapter_num in range(first_chapter, last_chapter + 1):
        try:
            print(f"Downloading chapter {chapter_num}...")
            chapter_text = scraper_manager.scrape_chapter(url, chapter_num)
            all_chapters.append(chapter_text)
            time.sleep(2)  # Be nice to the server
        except ValueError as e:
            print(f"Warning: Failed to download chapter {chapter_num}")
            continue

    if all_chapters:
        print("\nConverting to EPUB...")
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        output_filename = f"{novel_info['title'].lower().replace(' ', '_')}_ch{first_chapter}-{last_chapter}.epub"
        output_path = os.path.join(output_dir, output_filename)
        
        # Create EPUB
        epub_manager.create_epub(novel_info, all_chapters, output_path)
        print(f"\nEPUB file created successfully to: {output_path}")
    else:
        print("\nNo chapters were downloaded. EPUB creation skipped.")

if __name__ == "__main__":
    main()