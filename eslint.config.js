module.exports = [
    {
        languageOptions:{
            ecmaVersion: 6,
            sourceType: "module",
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
