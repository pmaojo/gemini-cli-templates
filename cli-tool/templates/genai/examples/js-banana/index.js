import { GoogleGenAI } from "@google/genai";
import fs from "fs";
import path from "path";

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error("Error: GEMINI_API_KEY environment variable not set.");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

async function generateImage(prompt, model = "gemini-3-pro-image-preview", outputFile = "output.png") {
  console.log(`Generating image with ${model}...`);
  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: prompt,
    });

    if (response.candidates && response.candidates.length > 0) {
      for (const part of response.candidates[0].content.parts) {
        if (part.inlineData) {
          const buffer = Buffer.from(part.inlineData.data, "base64");
          fs.writeFileSync(outputFile, buffer);
          console.log(`Image saved to ${outputFile}`);
          return true;
        }
      }
    }

    console.log("No image data found in response.");
    return false;

  } catch (error) {
    console.error(`Error generating image: ${error.message}`);
    return false;
  }
}

async function main() {
  const prompt = "A futuristic city with neon signs saying 'Gemini 3' and 'Banana Pro'";

  // Try Nano Banana Pro (Gemini 3 Pro Image)
  await generateImage(prompt, "gemini-3-pro-image-preview", "gemini_3_pro.png");

  // Try Nano Banana (Gemini 2.5 Flash Image)
  await generateImage(prompt, "gemini-2.5-flash-image", "gemini_2_5_flash.png");
}

main();
