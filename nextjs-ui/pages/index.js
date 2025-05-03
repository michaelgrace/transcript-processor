import { Box, Heading, Text } from "@chakra-ui/react";

export default function Home() {
  return (
    <Box p={8}>
      <Heading mb={4}>Transcript Processor (Next.js + Chakra UI)</Heading>
      <Text>
        Welcome! Start building your new frontend here. Use Chakra UI components and connect to your FastAPI backend using the API helper.
      </Text>
    </Box>
  );
}
