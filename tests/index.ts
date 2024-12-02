import type { z } from "zod";
import { readFileSync } from "node:fs";
import compareResponseSchema from "./schemas";

type CompareResponse = z.infer<typeof compareResponseSchema>;

async function main() {
	try {
		// Read PDF files
		const file1 = new File(
			[
				readFileSync(
					"/Users/suryavirkapur/Projekts/plgrzr/data/plgrzr_cleaned_dataset/prz_r63ud8rc.pdf",
				),
			],
			"prz_r63ud8rc.pdf",
			{ type: "application/pdf" },
		);

		const file2 = new File(
			[
				readFileSync(
					"/Users/suryavirkapur/Projekts/plgrzr/data/plgrzr_cleaned_dataset/prz_zygw1g26.pdf",
				),
			],
			"prz_zygw1g26.pdf",
			{ type: "application/pdf" },
		);

		const result = await compareDocuments(file1, file2, 0.5);
		console.log(JSON.stringify(result, null, 2));
	} catch (error) {
		console.error("Error comparing documents:", error);
	}
}

const compareDocuments = async (
	file1: File,
	file2: File,
	weightText: number,
): Promise<CompareResponse> => {
	const formData = new FormData();
	formData.append("file1", file1);
	formData.append("file2", file2);
	formData.append("weight_text", weightText.toString());

	const response = await fetch("http://localhost:5001/compare", {
		method: "POST",
		body: formData,
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.error || "An error occurred during comparison");
	}

	const data = await response.json();
	const result = compareResponseSchema.parse(data);

	return result;
};

main();
