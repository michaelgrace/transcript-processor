import { Box, Heading, Text } from "@chakra-ui/react";

export default function Home() {
  return (
    <Box p={8}>
      <Heading mb={4}>Transcript Processor (Next.js + Chakra UI)</Heading>
      <Text>
        Welcome! Start building your new frontend here. <br />
        Use Chakra UI components. Connect to your FastAPI backend using the API helper.
      </Text>
    </Box>
  );
}
