import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

// Create the app *first*
const app = createApp(App);

// Then use plugins
app.use(router);
app.use(Toast);

// Then mount
app.mount("#app");

// Credits: marudev