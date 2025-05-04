import { extendTheme } from "@chakra-ui/react";

const theme = extendTheme({
  config: {
    initialColorMode: "dark",
    useSystemColorMode: false,
    storage: "memory", // disables localStorage/cookie persistence
  },
});

export default theme;
