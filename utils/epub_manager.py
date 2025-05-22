import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import requests
import os

def create_epub(novel_info, chapters, output_path):
    """
    Create an EPUB book from the novel information and chapters.
    
    Args:
        novel_info (dict): Dictionary containing novel metadata
        chapters (list): List of chapter contents
        output_path (str): Path where the EPUB file should be saved
    """
    # Create a new EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(f"id_{novel_info['title'].lower().replace(' ', '_')}")
    book.set_title(novel_info['title'])
    book.set_language('en')
    book.add_author(novel_info['author'])

    # Add cover image if available
    if novel_info.get('cover_image'):
        try:
            # Download the cover image
            response = requests.get(novel_info['cover_image'])
            if response.status_code == 200:
                # Create a temporary file for the cover
                cover_path = os.path.join(os.path.dirname(output_path), 'temp_cover.jpg')
                with open(cover_path, 'wb') as f:
                    f.write(response.content)
                
                # Add the cover to the EPUB
                book.set_cover('cover.jpg', open(cover_path, 'rb').read())
                
                # Clean up the temporary file
                os.remove(cover_path)
        except Exception as e:
            print(f"Warning: Could not add cover image: {str(e)}")

    # Create novel information chapter
    info_chapter = epub.EpubHtml(title='Novel Information',
                                file_name='novel_info.xhtml',
                                lang='en')
    
    # Format novel information
    info_content = f'''
    <h1>{novel_info['title']}</h1>
    <h2>Novel Information</h2>
    <div class="novel-info">
        <p><strong>Author:</strong> {novel_info['author']}</p>
        <p><strong>Genre:</strong> {novel_info['genre']}</p>
    '''
    
    # Add description if available
    if novel_info.get('description'):
        info_content += f'<h3>Description</h3><p>{novel_info["description"]}</p>'
    
    # Add any additional metadata if available
    for key, value in novel_info.items():
        if key not in ['title', 'author', 'genre', 'description', 'cover_image']:
            info_content += f'<p><strong>{key.title()}:</strong> {value}</p>'
    
    info_content += '</div>'
    info_chapter.content = info_content
    book.add_item(info_chapter)

    # Create chapters
    epub_chapters = []
    for i, chapter_content in enumerate(chapters, 1):
        # Split content into title and body
        lines = chapter_content.split('\n', 1)
        chapter_title = lines[0].strip()
        chapter_body = lines[1] if len(lines) > 1 else ""
        
        # Create chapter
        chapter = epub.EpubHtml(title=chapter_title,
                              file_name=f'chapter_{i}.xhtml',
                              lang='en')
        
        # Clean and format chapter content
        soup = BeautifulSoup(chapter_body, 'html.parser')
        
        # Split content into paragraphs and wrap each in p tags
        paragraphs = chapter_body.split('\n\n')
        formatted_content = f'<h1>{chapter_title}</h1>'
        for para in paragraphs:
            if para.strip():  # Only add non-empty paragraphs
                formatted_content += f'<p>{para.strip()}</p>'
        
        chapter.content = formatted_content
        
        # Add chapter to book
        book.add_item(chapter)
        epub_chapters.append(chapter)

    # Create table of contents
    book.toc = [info_chapter] + epub_chapters

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    body {
        font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
        line-height: 1.5;
        padding: 1em;
        margin: 0;
    }
    h1 {
        text-align: center;
        margin-bottom: 1em;
    }
    h2 {
        text-align: center;
        margin: 1em 0;
    }
    h3 {
        margin: 1em 0 0.5em 0;
    }
    p {
        text-align: justify;
        margin: 0.5em 0;
    }
    .novel-info {
        margin: 2em 0;
    }
    '''
    
    # Add CSS file
    css = epub.EpubItem(uid="style_default",
                        file_name="style/default.css",
                        media_type="text/css",
                        content=style)
    book.add_item(css)

    # Create spine
    book.spine = ['nav', info_chapter] + epub_chapters

    # Write EPUB file
    epub.write_epub(output_path, book, {})
