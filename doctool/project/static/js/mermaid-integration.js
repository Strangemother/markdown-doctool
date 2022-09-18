const MUSTARD = '#6c610e';
const NEARLY_BLACK = "#040404";
const GREEN ='#0f7642';

mermaid.initialize({
    startOnLoad: true,
    securityLevel: 'loose',
    theme: 'base',

    themeVariables: {
        /* Default background color for graphs */
        background: NEARLY_BLACK,
        primaryColor: "#000",
        primaryBorderColor: "#111",
        primaryTextColor: GREEN,
        secondaryColor: NEARLY_BLACK,
        noteBkgColor: NEARLY_BLACK,
        noteTextColor: MUSTARD,
        /*Alter Alice John and Bob cell background for a sequenceDiagram.*/
        mainBkg: NEARLY_BLACK,

        // textColor: '#ff0000',
        lineColor: '#6c610e',
        fontFamily: 'inherit',
        // fontSize: 'inherit',
        darkMode: true,
    }
});
