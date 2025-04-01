import CMS from 'decap-cms';

// Register LaTeX component
CMS.registerEditorComponent({
  id: 'latex',
  label: 'LaTeX',
  pattern: /^\$\$(.*?)\$\$|\$(.*?)\$/s,
  fromBlock: function(match) {
    return {
      latex: match[1] || match[2],
      display: !!match[1]
    };
  },
  toBlock: function(data) {
    const delimiter = data.display ? '$$' : '$';
    return `${delimiter}${data.latex}${delimiter}`;
  },
  toPreview: function(data) {
    const delimiter = data.display ? '$$' : '$';
    return `${delimiter}${data.latex}${delimiter}`;
  }
}); 