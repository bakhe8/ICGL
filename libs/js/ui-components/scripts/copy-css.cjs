const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "src");
const DIST = path.join(__dirname, "..", "dist");

function copyCssFiles(srcDir, distDir) {
  const entries = fs.readdirSync(srcDir, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name);
    const distPath = path.join(distDir, entry.name);
    if (entry.isDirectory()) {
      copyCssFiles(srcPath, distPath);
    } else if (entry.isFile() && entry.name.endsWith(".css")) {
      fs.mkdirSync(path.dirname(distPath), { recursive: true });
      fs.copyFileSync(srcPath, distPath);
      console.log(`Copied ${srcPath} -> ${distPath}`);
    }
  }
}

copyCssFiles(SRC, DIST);
