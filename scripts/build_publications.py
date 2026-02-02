import os
import glob
import re

def load_coauthors():
    """Simple parser for the specific coauthor_profile.yml format"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yml_path = os.path.join(script_dir, 'coauthor_profile.yml')
    
    coauthors = {}
    if not os.path.exists(yml_path):
        return coauthors

    current_name = None
    with open(yml_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- name:'):
                current_name = line.split(':', 1)[1].strip()
            elif line.startswith('link:') and current_name:
                link = line.split(':', 1)[1].strip()
                coauthors[current_name] = link
                current_name = None
    return coauthors

def get_publications():
    # Helper to find data dir relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '../data')
    
    bib_files = glob.glob(os.path.join(data_dir, '*.bib'))
    pubs = []
    
    for bib_file in bib_files:
        with open(bib_file, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                continue
            
            # Extract fields
            title_m = re.search(r'title\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE | re.DOTALL)
            author_m = re.search(r'author\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE | re.DOTALL)
            year_m = re.search(r'year\s*=\s*[{\"](\d+)[}\"]', content, re.IGNORECASE)
            journal_m = re.search(r'(journal|booktitle)\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE)
            note_m = re.search(r'note\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE | re.DOTALL)
            webpage_m = re.search(r'webpage\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE)
            link_m = re.search(r'link\s*=\s*[{\"](.*?)[}\"]', content, re.IGNORECASE)

            if title_m and author_m and year_m:
                title = title_m.group(1).replace('{', '').replace('}', '').strip()
                authors = re.sub(r'\s+', ' ', author_m.group(1)).strip()
                year = int(year_m.group(1))
                venue = journal_m.group(2).replace('{', '').replace('}', '').strip() if journal_m else "Preprint"
                note = note_m.group(1).strip() if note_m else ""
                webpage = webpage_m.group(1).strip() if webpage_m else ""
                link = link_m.group(1).strip() if link_m else ""
                
                base_name = os.path.splitext(os.path.basename(bib_file))[0]
                image_path = f"images/{base_name}.png" 
                
                pubs.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': venue,
                    'note': note,
                    'webpage': webpage,
                    'base_name': base_name,
                    'image_path': image_path,
                    'link': link
                })
    
    pubs.sort(key=lambda x: x['year'], reverse=True)
    return pubs

def generate_html(pubs):
    html = ""
    my_name = "Weihang Guo"
    coauthors = load_coauthors()
    # Normalize coauthor keys for easier matching (remove dots)
    coauthors_norm = {k.replace('.', ''): v for k, v in coauthors.items()}
    
    for pub in pubs:
        # Puts authors in a list
        raw_authors = [a.strip() for a in pub['authors'].split(' and ')]
        formatted_authors = []
        
        for auth in raw_authors:
            # Handle "Last, First" format
            if ',' in auth:
                parts = auth.split(',', 1)
                last = parts[0].strip()
                first = parts[1].strip()
                name = f"{first} {last}"
            else:
                name = auth
            
            # Normalize for matching (remove dots)
            name_clean = name.replace('.', '')
            
            if name_clean == my_name.replace('.', ''):
                formatted_authors.append(f"<strong>{my_name}</strong>")
            elif name_clean in coauthors_norm:
                # Use the original name from YAML if possible, or the flipped one
                # But here we just want to link the name we displayed.
                # Actually, better to use the display name from the Bib file but linked? 
                # Or use the "nice" name from YAML? 
                # Let's use the nice name (key in original dict) if we can find it, or just link the flipped name.
                # To find the original key:
                original_key = next((k for k in coauthors if k.replace('.', '') == name_clean), name)
                formatted_authors.append(f"<a href=\"{coauthors_norm[name_clean]}\">{original_key}</a>")
            else:
                formatted_authors.append(name)
                
        auth_str = ", ".join(formatted_authors)
        
        # Link title if webpage exists
        title_html = pub['title']
        title_html = f'<span class="papertitle">{pub["title"]}</span>'

        # Build dynamic links section
        links_html = ""
        # You could add logic here to add project page / arxiv links if they were in the bib
        # For now, per instructions, we purely rely on 'webpage' or 'note' for extra info.
        # If the user wants specific "project page" or "arXiv" links separated, they might need specific bib fields.
        # For now, I will remove the hardcoded ones.
        
        # Note section
        description_html = ""
        if pub['note']:
            description_html = f"<p>{pub['note']}</p>"
        if pub['webpage']:
            description_html += f"<p><a href=\"{pub['webpage']}\">Project Page</a></p>"
        if pub['link']:
            description_html += f"<p><a href=\"{pub['link']}\">Paper</a></p>"
        entry_html = f"""
          <table style="width:100%;border:0px;border-spacing:0px 10px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:16px;width:20%;vertical-align:middle">
                <div class="one">
                  <img src='{pub['image_path']}' width="160">
                </div>
              </td>
              <td style="padding:8px;width:80%;vertical-align:middle">
                {title_html}
                <br>
                {auth_str}
                <br>
                <em>{pub['venue']}</em>, {pub['year']}
                <br>
                {links_html}
                {description_html}
              </td>
            </tr>
          </tbody></table>
"""
        html += entry_html
        
    return html

if __name__ == "__main__":
    pubs = get_publications()
    print(generate_html(pubs))
