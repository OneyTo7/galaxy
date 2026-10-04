/// <reference types="vite/client" />

declare module 'monaco-editor/esm/vs/editor/editor.worker?worker' {
  const editorWorker: {
    new (): Worker
  }
  export default editorWorker
}
