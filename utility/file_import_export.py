
import base64


def create_download_link(string, filename, text):
    # Encode the string as bytes
    string_bytes = string.encode('utf-8')
    
    # Create a base64 representation of the bytes
    base64_str = base64.b64encode(string_bytes).decode('utf-8')
    
    # Create the download link
    href = f'<a href="data:file/txt;base64,{base64_str}" download="{filename}">{text}</a>'
    return href