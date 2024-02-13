const js = require("@eslint/js");
const globals = require("globals");

module.exports = [
    js.configs.recommended,
    {
        files: ["**/*.js"],
        languageOptions:{
            ecmaVersion: "latest",
            sourceType: "module",
            globals: {
                ...globals.browser,
                ...globals.node
            }
        }
    },
    {
        rules: {
            "curly": ["error", "all"],
            "dot-notation": "error",
            "eqeqeq": "error",
            "no-eval": "error",
            "no-var": "error",
            "prefer-const": "error",
            "semi": "error"
        }
    }
];
