module.exports = {
    "env": {
        "browser": true,
        "es6": true,
        node: true,
    },
    "extends": "eslint:recommended",
    "parserOptions": {
        "ecmaVersion": 6,
        "sourceType": "module"
    },
    "rules": {
        "curly": ["error", "all"],
        "dot-notation": "error",
        "eqeqeq": "error",
        "no-eval": "error",
        "no-var": "error",
        "prefer-const": "error",
        "semi": "error"
    }
};
