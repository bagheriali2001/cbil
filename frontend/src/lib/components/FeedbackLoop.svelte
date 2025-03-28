<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { selectedFeatures } from '$lib/store/store.js';

	type ResultItem = {
		file: string;
		_score: number;
	};

	export let feedbackImages: Array<string> = [];

	let selectedImageUrl: string | null = null;
	let result: ResultItem[] | null = null;
	let isLoading = false;
	let isError = false;
	let selectedResults: Array<string> = [];
	const dispatch = createEventDispatcher();

	const getFeedback = async () => {
		let urls = feedbackImages;
		if (urls.length == 0) return;

		isError = false;
		isLoading = true;
		result = null;

		try {
			const response = await fetch(`${PUBLIC_API_URL}/feedback`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ file_keys: urls, features: $selectedFeatures })
			});
			const data = await response.json();

			if (response.ok) {
				result = data;
			} else {
				console.error('Processing failed:', data);
			}
		} catch (error) {
			isError = true;
			console.error('Error processing image:', error);
		} finally {
			isLoading = false;
		}
	};

	if (feedbackImages.length > 0) {
		getFeedback();
	}

	const resetSelection = () => {
		feedbackImages = [];
		selectedResults = [];
		selectedImageUrl = null;
		result = null;
		dispatch('resetSearch');
	};

	const toggleSelection = (item: any) => {
		const index = selectedResults.findIndex((selected) => selected === item.file);
		if (index === -1) {
			selectedResults = [...selectedResults, item.file];
		} else {
			selectedResults = selectedResults.filter((selected) => selected !== item.file);
		}
	};

	const updateResults = () => {
		feedbackImages = selectedResults;
		selectedResults = [];
		getFeedback();
	};
</script>

<div class="results">
	<div class="container">
		<div class="left-panel">
			<div class="image-grid-l">
				{#each feedbackImages as url, index}
					<div class="image-container">
						<img src={url} alt="Result file" class="grid-image" />
					</div>
				{/each}
			</div>
		</div>

		<div class="divider" />

		<div class="right-panel">
			{#if isLoading}
				<p>Loading results...</p>
			{:else if isError}
				<p>The response has an error, Please retry!</p>
			{:else if result && result.length > 0}
				<div class="image-grid">
					{#each result.slice(0, 10) as item, index}
						<div
							class="image-container"
							role="button"
							tabindex="0"
							on:click={() => toggleSelection(item)}
							on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && toggleSelection(item)}
						>
							<div class="image-overlay-l">
								<span>#{index + 1}</span>
							</div>
							<div class="image-overlay-r">
								<span>Score: {Math.trunc(item._score * 100) / 100}</span>
							</div>
							<img
								src={item.file}
								alt="Result file"
								class="grid-image {selectedResults.some((selected) => selected === item.file)
									? 'selected'
									: ''}"
							/>
						</div>
					{/each}
				</div>
			{:else}
				<p>No results found.</p>
			{/if}
		</div>
	</div>

	<div class="button-group">
		<button on:click={resetSelection} class="reset-btn">Upload Another Image</button>
		<button on:click={getFeedback} class="retry-btn">Retry Upload</button>
		{#if selectedResults.length > 0}
			<button on:click={updateResults} class="update-btn">Update the Results</button>
		{/if}
	</div>
</div>

<style lang="scss">
	.results {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 15px;
		width: 100%;

		.container {
			display: flex;
			width: 100%;
			max-width: 900px;
			gap: 20px;
		}

		.left-panel {
			flex: 40%;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: flex-start;
		}

		.right-panel {
			flex: 60%;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
		}

		.image-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
			grid-template-columns: repeat(4, 1fr);
			gap: 10px;
			width: 100%;
		}

		.image-grid-l {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
			grid-template-columns: repeat(2, 1fr);
			gap: 10px;
			width: 100%;
		}

		.grid-image {
			width: 100%;
			height: 100px;
			object-fit: cover;
			border-radius: 5px;
			box-shadow: 0 2px 4px var(--box-shadow-primary);
			cursor: pointer;
			transition: border 0.3s ease, transform 0.2s ease;
			border: 2px solid transparent;
		}

		.grid-image:hover {
			transform: scale(1.05);
		}

		.grid-image.selected {
			border: 3px solid var(--select-primary);
			box-shadow: 0 0 8px var(--select-primary-shadow);
		}

		.button-group {
			margin-top: 20px;
			display: flex;
			gap: 10px;
		}

		.reset-btn,
		.update-btn,
		.retry-btn {
			padding: 10px 20px;
			font-size: 16px;
			border-radius: 5px;
			cursor: pointer;
			transition: background-color 0.3s ease;
			border: none;
			color: var(--light-0);
		}

		.reset-btn {
			background-color: var(--reset-primary);
		}

		.reset-btn:hover {
			background-color: var(--reset-primary-hover);
		}

		.update-btn {
			background-color: var(--update-primary);
		}

		.update-btn:hover {
			background-color: var(--update-primary-hover);
		}

		.retry-btn {
			background-color: var(--features-primary);
		}

		.retry-btn:hover {
			background-color: var(--features-primary-hover);
		}
	}

	.image-container {
		position: relative;
		display: flex;
	}

	.image-overlay-r,
	.image-overlay-l {
		position: absolute;
		top: 5px;
		background: var(--img-overlay-primary);
		color: var(--img-overlay-text);
		font-size: 12px;
		padding: 4px 6px;
		border-radius: 4px;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		z-index: 10;
	}

	.image-overlay-r {
		right: 5px;
	}
	.image-overlay-l {
		left: 5px;
	}

	.image-overlay span {
		display: block;
	}

	.divider {
		width: 1px;
		background-color: var(--divider-primary);
		align-self: stretch;
	}
</style>
