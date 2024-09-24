import * as fs from 'fs';
import * as path from 'path';
import _ from 'lodash';

const inputFiles = fs.readdirSync('.')
  .filter((file) => file.endsWith('.jsonl')); // Filter for JSONL files

console.log('Found input files:', inputFiles);

let id = 0;
const allLines = [];


for (const inputFile of inputFiles) {
   
   console.log(`PARSING FILE ------------------------- : ${inputFile}`);

   const fileStream = fs.createReadStream(inputFile);
   fileStream.on('line', (line) => {
     
     const parsedLine: { conversation: string } = JSON.parse(line); // Assuming parsedLine is of type { conversation: string }
     const text = parsedLine.conversation;
     const array = text.split(/(Samantha:|Theodore:)/)
     .map(s => s.trim())
     .filter((s) => s.length > 0); 
  
     const convo = {
       id,
       conversations: _.chunk(array, 2).map((match) => ({
         from: { "Erik:": "human", "Greta:": "gpt" }[(match[0] as string).trim()],
         value: (match[1] as string).trim(),
       })),
     };
     
     allLines.push(JSON.stringify(convo));
     id++;
  
   });
   
   fileStream.on('end', () => {
     console.log(`Finished processing ${inputFile}`);
   });
}

console.log(`Number of conversations in allLines: ${allLines.length}`);
   
// Wait for all files to be processed
//Promise.all(inputFiles.map((file) => new Promise((resolve) => fs.createReadStream(file).on('end', resolve))))
//   .then(() => {
//     fs.writeFileSync('greta_conv_2024_03_22.jsonl', allLines.join('\n'));
//     console.log('All conversations saved to out_results.jsonl');
//   })
//   .catch((error) => {
//    console.error('Error processing files:', error);
//   });
