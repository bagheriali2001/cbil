<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
	console.log('PUBLIC_API_URL: ', PUBLIC_API_URL);

	export let selectedImage: File | null;

	let result: Array<Object> | null = null;
	let isLoading = false;
	let localImagePreview: string | null = null;
	let selectedResults: Array<Object> = [];
	const dispatch = createEventDispatcher();

	const uploadImage = async () => {
		if (!selectedImage) return;

		isLoading = true;
		const formData = new FormData();
		formData.append('image', selectedImage);

		try {
			const response = await fetch(`${PUBLIC_API_URL}/upload`, {
				method: 'POST',
				body: formData
			});
			const data = await response.json();

			if (response.ok) {
				result = data;
				console.log('Response:', data);
			} else {
				console.error('Upload failed:', data);
			}
		} catch (error) {
			console.error('Error uploading image:', error);
		} finally {
			isLoading = false;
		}
	};

	if (selectedImage) {
		localImagePreview = URL.createObjectURL(selectedImage);
		uploadImage();
	}

	const resetSelection = () => {
		console.log('Handle Reset !!');
		localImagePreview = null;
		dispatch('resetSearch');
	};

	// Function to select/deselect an image
	const toggleSelection = (item: any) => {
		const index = selectedResults.findIndex((selected) => selected === item.file);
		if (index === -1) {
			selectedResults = [...selectedResults, item.file]; // Add image to selection
		} else {
			selectedResults = selectedResults.filter((selected) => selected !== item.file); // Remove from selection
		}
		console.log('selectedResults: ', selectedResults);
	};

	// Function to dispatch selected images
	const startFeedbackLoop = () => {
		dispatch('startFeedbackLoop', { selectedResults });
	};
</script>

<div class="results">
	<div class="container">
		<div class="left-panel">
			<!-- svelte-ignore a11y-img-redundant-alt -->
			<img src={localImagePreview} alt="Selected image preview" class="preview" />
		</div>

		<div class="divider" />

		<div class="right-panel">
			{#if result && result.length > 0}
				<div class="image-grid">
					<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
					<!-- svelte-ignore a11y-img-redundant-alt -->
					{#each result.slice(0, 10) as item, index}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div class="image-container" on:click={() => toggleSelection(item)}>
							<div class="image-overlay-l">
								<span>#{index + 1}</span>
							</div>
							<div class="image-overlay-r">
								<span>Score: {Math.trunc(item._score * 100) / 100}</span>
							</div>

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
		<button on:click={resetSelection} class="reset-btn">Upload Another Image</button>
		{#if selectedResults.length > 0}
			<button on:click={startFeedbackLoop} class="update-btn">Update the results</button>
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

		h2 {
			color: var(--primary-text);
		}

		.container {
			display: flex;
			width: 100%;
			max-width: 900px;
			gap: 20px;
		}

		.left-panel {
			flex: 25%;
			display: flex;
			align-items: center;
			justify-content: center;

			.preview {
				max-width: 100%;
				max-height: 300px;
				border-radius: 8px;
				box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
			}
		}

		.right-panel {
			flex: 75%;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
		}

		.image-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
			grid-template-columns: repeat(5, 1fr); /* Ensures max 5 columns */
			gap: 10px;
			width: 100%;
			max-width: 100%;
		}

		.grid-image {
			width: 100%;
			height: 100px;
			object-fit: cover;
			border-radius: 5px;
			box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
			cursor: pointer;
			transition: border 0.3s ease, transform 0.2s ease;
		}

		.grid-image:hover {
			transform: scale(1.05);
		}

		/* Selected Image */
		.grid-image.selected {
			border: 3px solid #28a745; /* Green border */
			box-shadow: 0 0 8px rgba(40, 167, 69, 0.7);
		}

		.loader {
			width: 50px;
			height: 50px;
			border: 5px solid rgba(0, 0, 0, 0.1);
			border-top: 5px solid var(--primary);
			border-radius: 50%;
			animation: spin 1s linear infinite;
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
		.update-btn {
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
	}
	.image-container {
		position: relative;
		display: flex;
	}

	.image-overlay-r {
		position: absolute;
		top: 5px;
		right: 5px;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		font-size: 12px;
		padding: 4px 6px;
		border-radius: 4px;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		z-index: 10;
	}
	.image-overlay-l {
		position: absolute;
		top: 5px;
		left: 5px;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		font-size: 12px;
		padding: 4px 6px;
		border-radius: 4px;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		z-index: 10;
	}

	.image-overlay span {
		display: block;
	}

	.divider {
		width: 1px; /* Thickness of the line */
		background-color: #929292; /* Gray color */
		align-self: stretch;
	}
</style>
