const fs = require('fs');
const path = require('path');

const ignorePatterns = [/node_modules/, /venv/, /__pycache__/];

function generateTree(dir, depth = 0) {
    const items = fs.readdirSync(dir, { withFileTypes: true });
    let tree = '';
    for (const item of items) {
        if (ignorePatterns.some(pattern => pattern.test(item.name))) continue;
        tree += `${' '.repeat(depth * 2)}- ${item.name}\n`;
        if (item.isDirectory()) {
            tree += generateTree(path.join(dir, item.name), depth + 1);
        }
    }
    return tree;
}

const tree = generateTree('.');
fs.writeFileSync('directory_structure.txt', tree);
console.log('Directory structure saved to directory_structure.txt');
