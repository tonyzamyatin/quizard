const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/flashcards',
        createProxyMiddleware({
            target: 'http://localhost:5000',
            changeOrigin: true,
            logLevel: 'debug',
            onError: (err, req, res) => {
                console.error('Proxy error:', err);
            },
        })
    );
}