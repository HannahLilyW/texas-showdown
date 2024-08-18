This is the backend.

## Local development on windows

### First time setup
1. Set up venv by doing the following from this directory in cmd:

```
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

2. Configure development proxy in vue-project/vite.config.ts by adding the server object below:

```javascript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/texas_api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/texas_api/, ''),
        ws: true
      }
    }
  }
})
```

### Subsequent development
From this directory do

```
.\env\Scripts\activate
cd texas
python manage.py runserver
```
