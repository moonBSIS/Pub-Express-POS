const { app, BrowserWindow, Menu, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const net = require("net");

const isDev = process.env.NODE_ENV === "development" || process.defaultApp;

const backendExe = isDev
  ? path.join(__dirname, "../backend/dist/fastapi-backend.exe")
  : path.join(process.resourcesPath, "fastapi-backend.exe");

// Check port utility
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once("error", () => resolve(false));
    server.once("listening", () => {
      server.close();
      resolve(true);
    });
    server.listen(port);
  });
}

async function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    icon: path.join(__dirname, "icon.ico"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (isDev) {
    // 🔥 Use Vite dev server in development
    await mainWindow.loadURL("http://localhost:5173"); // Change this if Vite runs on a different port
    mainWindow.webContents.openDevTools(); // Optional: open devtools automatically
  } else {
    // ✅ Production build
    await mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  // Start FastAPI backend if not already running
  const portFree = await isPortAvailable(8000);
  if (portFree) {
    console.log("Port 8000 available. Launching backend...");
    const backendProcess = spawn(backendExe, [], {
      cwd: isDev ? path.dirname(backendExe) : process.resourcesPath,
      detached: true, // ✅ Important to prevent Electron from killing it early
      stdio: "inherit",
      shell: true,
    });

    // ✅ Pipe output to Electron's console
    backendProcess.stdout.on("data", (data) => {
      console.log(`[Backend] ${data}`);
    });

    backendProcess.stderr.on("data", (data) => {
      console.error(`[Backend ERROR] ${data}`);
    });

    backendProcess.on("close", (code) => {
      console.log(`[Backend exited with code ${code}]`);
    });
    backendProcess.unref(); // ✅ Important to let it run independently
  } else {
    console.log("Backend already running on port 8000.");
  }
}

const template = [
  {
    label: "File",
    submenu: [{ role: "quit" }],
  },
  {
    label: "View",
    submenu: [
      { role: "reload" },
      { role: "forceReload" },
      { role: "toggleDevTools" },
      { type: "separator" },
      { role: "resetZoom" },
      { role: "zoomIn" },
      { role: "zoomOut" },
      { type: "separator" },
      { role: "togglefullscreen" },
    ],
  },
  {
    label: "Window",
    submenu: [{ role: "minimize" }, { role: "close" }],
  },
  {
    label: "Help",
    submenu: [
      {
        label: "Contact Support",
        click: async () => {
          await shell.openExternal("mailto:anthonyclyde.melendez@gmail.com");
        },
      },
      {
        label: "Visit Website",
        click: async () => {
          await shell.openExternal(
            "https://www.linkedin.com/in/anthonyclyde-melendez"
          );
        },
      },
      { type: "separator" },
      { role: "about" },
    ],
  },
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

app.setAboutPanelOptions({
  applicationName: "Pub Express POS",
  applicationVersion: "5.17.25",
  copyright: "© 2025 marudev",
  authors: ["Anthony Clyde P. Melendez"],
  website: "www.linkedin.com/in/anthonyclyde-melendez",
});

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
