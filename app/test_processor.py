def adjust_markdown_headings(markdown_text):
	"""
	Adjust markdown headings:
	- `#` becomes `##`
	- `##` becomes `###`
	- Default heading level is `##`
	"""
	lines = markdown_text.splitlines()
	adjusted_lines = []
	for line in lines:
		if line.startswith("###"):
			adjusted_lines.append(line)  # Keep ### as is
		elif line.startswith("##"):
			adjusted_lines.append("#" + line)  # Convert ## to ###
		elif line.startswith("#"):
			adjusted_lines.append("#" + line)  # Convert # to ##
		else:
			adjusted_lines.append(line)  # Keep other lines as is
	return "\n".join(adjusted_lines)


# Example usage
if __name__ == "__main__":
	sample_markdown = """# Heading 1
## Heading 2
### Heading 3
Normal text"""
	print(adjust_markdown_headings(sample_markdown))

# Output:
# ## Heading 1  # Converted from # to ##
# ### Heading 2  # Converted from ## to ###

def detect_and_process(content, filename, add_paragraphs=True, add_headings=True, 
                      fix_grammar=True, highlight_key_points=True, format_style="Article"):
    # Existing code...
    
    # Adjust heading sizes as the final step
    processed_content = adjust_markdown_headings(processed_content)
    
    return processed_content














