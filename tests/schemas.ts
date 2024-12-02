import { z } from "zod";

const featureScoresSchema = z.object({
	confidence_similarity: z.number(),
	symbol_density_similarity: z.number(),
	line_break_similarity: z.number(),
	average_confidence_similarity: z.number(),
});

const changeSchema = z.object({
	type: z.string(),
	difference: z.number(),
	description: z.string(),
});

const variationSchema = z.object({
	from_page: z.number(),
	to_page: z.number(),
	changes: z.array(changeSchema),
});

const anomalySchema = z.object({
	confidence: z.optional(
		z.object({
			value: z.number(),
			mean: z.number(),
			deviation: z.number(),
		}),
	),
	symbol_density: z.optional(
		z.object({
			value: z.number(),
			mean: z.number(),
			deviation: z.number(),
		}),
	),
	line_breaks: z.optional(
		z.object({
			value: z.number(),
			mean: z.number(),
			deviation: z.number(),
		}),
	),
	paragraph_index: z.number(),
	page_number: z.number(),
});

const compareResponseSchema = z.object({
	text_similarity: z.number(),
	text_consistency: z.object({
		doc1: z.array(
			z.object({
				segment_index: z.number(),
				segment_text: z.string(),
				next_segment_text: z.string(),
				similarity_score: z.number(),
			}),
		),
		doc2: z.array(
			z.object({
				segment_index: z.number(),
				segment_text: z.string(),
				next_segment_text: z.string(),
				similarity_score: z.number(),
			}),
		),
	}),
	handwriting_similarity: z.number(),
	similarity_index: z.number(),
	feature_scores: featureScoresSchema,
	anomalies: z.object({
		document1: z.array(anomalySchema),
		document2: z.array(anomalySchema),
	}),
	variations: z.object({
		document1: z.array(variationSchema),
		document2: z.array(variationSchema),
	}),
	report_url: z.string(),
});

export default compareResponseSchema;
