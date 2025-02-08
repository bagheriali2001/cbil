// store.js
import { writable } from "svelte/store";

// Store to track selected items
export const selectedFeatures = writable(['mean']);
