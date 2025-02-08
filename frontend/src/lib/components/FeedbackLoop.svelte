<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { selectedFeatures } from '$lib/store/store.js'; // Import the store

	export let feedbackImages: Array<string> = [];

	let selectedImageUrl: string | null = null;
	let result: Array<Object> | null = null;
	let isLoading = false;
	let selectedResults: Array<string> = [];
	const dispatch = createEventDispatcher();

	const getFeedback = async () => {
		let urls = feedbackImages;
		if (urls.length == 0) return;

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
						<!-- svelte-ignore a11y-img-redundant-alt -->
						<img src={url} alt="Result image" class="grid-image" />
					</div>
				{/each}
			</div>
		</div>

		<div class="divider" />

		<div class="right-panel">
			{#if isLoading}
				<p>Loading results...</p>
				<div class="loader" />
			{:else if result && result.length > 0}
				<div class="image-grid">
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					{#each result.slice(0, 10) as item, index}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<div class="image-container" on:click={() => toggleSelection(item)}>
							<div class="image-overlay-l">
								<span>#{index + 1}</span>
							</div>
							<div class="image-overlay-r">
								<span>Score: {Math.trunc(item._score * 100) / 100}</span>
							</div>
							<!-- svelte-ignore a11y-img-redundant-alt -->
							<img
								src={item.file}
								alt="Result image"
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
		<button on:click={resetSelection} class="reset-btn">Clear Selection</button>
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
			cursor: pointer;
			transition: border 0.3s ease, transform 0.2s ease;
			border: 2px solid transparent;
		}

		.grid-image:hover {
			transform: scale(1.05);
		}

		.grid-image.selected {
			border: 3px solid #28a745;
			box-shadow: 0 0 8px rgba(40, 167, 69, 0.7);
		}

		@keyframes spin {
			0% {
				transform: rotate(0deg);
			}
			100% {
				transform: rotate(360deg);
			}
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
			color: #ffffff;
		}

		.reset-btn {
			background-color: #444444;
		}

		.reset-btn:hover {
			background-color: #333333;
		}

		.update-btn {
			background-color: #28a745;
		}

		.update-btn:hover {
			background-color: #218838;
		}

		.retry-btn {
			background-color: #f0ad4e;
		}

		.retry-btn:hover {
			background-color: #ec971f;
		}
	}

	.loader {
		width: 50px;
		height: 50px;
		border: 5px solid rgba(0, 0, 0, 0.1);
		border-top: 5px solid var(--primary);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.image-container {
		position: relative;
		display: flex;
	}

	.image-overlay-l,
	.image-overlay-r {
		position: absolute;
		top: 5px;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		font-size: 12px;
		padding: 4px 6px;
		border-radius: 4px;
		display: flex;
		align-items: flex-start;
		z-index: 10;
	}

	.image-overlay-l {
		left: 5px;
	}

	.image-overlay-r {
		right: 5px;
	}

	.divider {
		width: 1px; /* Thickness of the line */
		background-color: #929292; /* Gray color */
		align-self: stretch;
	}
</style>
