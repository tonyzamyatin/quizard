// craco.config.js

module.exports = {
    webpack: {
        configure: {
            resolve: {
                fallback: {
                    fs: false,
                    path: require.resolve('path-browserify'),
                    crypto: require.resolve('crypto-browserify'),
                    // ... other polyfills
                },
            },
        },
    },
};
