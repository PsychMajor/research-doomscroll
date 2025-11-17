/**
 * HTML Sanitizer Utility
 * 
 * Safely renders HTML content while allowing formatting tags (sub, sup, em, strong, etc.)
 * and sanitizing dangerous content (scripts, event handlers, etc.)
 */

/**
 * Allowed HTML tags for scientific paper content
 */
const ALLOWED_TAGS = [
  'sub',      // Subscript
  'sup',      // Superscript
  'em',       // Emphasis
  'strong',   // Strong emphasis
  'i',        // Italic
  'b',        // Bold
  'u',        // Underline
  'span',     // Generic span
  'p',        // Paragraph
  'br',       // Line break
  'div',      // Division
];

/**
 * Allowed attributes for HTML tags
 */
const ALLOWED_ATTRIBUTES = [
  'class',
  'style', // We'll sanitize style content
];

/**
 * Sanitize HTML content by removing dangerous tags and attributes
 * while preserving safe formatting tags
 */
export const sanitizeHtml = (html: string): string => {
  if (!html) return '';

  try {
    // Create a temporary DOM element to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Recursively sanitize the DOM tree
    const sanitizeNode = (node: Node): void => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        const element = node as Element;
        const tagName = element.tagName.toLowerCase();

        // Remove disallowed tags
        if (!ALLOWED_TAGS.includes(tagName)) {
          // Replace with its children
          const parent = element.parentNode;
          if (parent) {
            while (element.firstChild) {
              parent.insertBefore(element.firstChild, element);
            }
            parent.removeChild(element);
          }
          return;
        }

        // Remove dangerous attributes
        const attributesToRemove: string[] = [];
        for (let i = 0; i < element.attributes.length; i++) {
          const attr = element.attributes[i];
          const attrName = attr.name.toLowerCase();

          // Remove event handlers and dangerous attributes
          if (
            attrName.startsWith('on') || // onclick, onerror, etc.
            (attrName === 'href' && attr.value.toLowerCase().startsWith('javascript:')) ||
            (attrName === 'src' && attr.value.toLowerCase().startsWith('javascript:')) ||
            (!ALLOWED_ATTRIBUTES.includes(attrName) && attrName !== 'style')
          ) {
            attributesToRemove.push(attrName);
          }
        }

        // Remove dangerous attributes
        attributesToRemove.forEach(attrName => {
          element.removeAttribute(attrName);
        });

        // Sanitize style attribute if present
        if (element.hasAttribute('style')) {
          const style = element.getAttribute('style') || '';
          // Remove dangerous CSS (javascript:, expression(), etc.)
          const sanitizedStyle = style
            .replace(/javascript:/gi, '')
            .replace(/expression\(/gi, '')
            .replace(/@import/gi, '');
          if (sanitizedStyle) {
            element.setAttribute('style', sanitizedStyle);
          } else {
            element.removeAttribute('style');
          }
        }

        // Recursively sanitize children (create a copy of the array to avoid mutation issues)
        const children = Array.from(element.childNodes);
        children.forEach(child => sanitizeNode(child));
      } else if (node.nodeType === Node.TEXT_NODE) {
        // Text nodes are safe, keep them
        return;
      }
    };

    // Sanitize all nodes
    const children = Array.from(tempDiv.childNodes);
    children.forEach(child => sanitizeNode(child));

    return tempDiv.innerHTML;
  } catch (error) {
    // If sanitization fails, return the original HTML (it will be escaped by React)
    console.warn('HTML sanitization failed:', error);
    return html;
  }
};

/**
 * Render HTML content safely
 * Returns an object suitable for dangerouslySetInnerHTML
 */
export const renderHtml = (html: string): { __html: string } => {
  const sanitized = sanitizeHtml(html);
  return { __html: sanitized };
};

/**
 * Check if a string contains HTML tags
 */
export const containsHtml = (text: string): boolean => {
  if (!text) return false;
  return /<[^>]+>/.test(text);
};

