<script lang="ts">
	import MainTitle from '$lib/components/MainTitle.svelte';
	import ImageUploader from '$lib/components/ImageUploader.svelte';
	import ShowResults from '$lib/components/ShowResults.svelte'; // Import the ShowResults component
	import FeedbackLoop from '$lib/components/FeedbackLoop.svelte';

	let selectedImage: File | null = null; // Declare a reactive variable for the selected image
	let feedbackImages: Array<string> = []; // Declare a reactive variable for the selected image
	let feedbackLoopStarted: boolean = false;

	const handleImageSelected = (event: CustomEvent) => {
		selectedImage = event.detail.file;
	};
	const handleUpdateFeedbackLoop = (event: CustomEvent) => {
		feedbackImages = event.detail.selectedResults;
		console.log('feedbackImages: ', feedbackImages);
		feedbackLoopStarted = true;
		selectedImage = null;
	};
	const handleReset = () => {
		console.log('Handle Reset !!');
		feedbackImages = [];
		selectedImage = null;
		feedbackLoopStarted = false;
	};
</script>

<svelte:head>
	<title>CBIL Search</title>
</svelte:head>

<div class="home">
	<div class="home-section">
		<MainTitle classes="!text-left">Welcome To CBIL Search</MainTitle>
		{#if selectedImage || feedbackLoopStarted}
			{#if feedbackLoopStarted}
				<FeedbackLoop
					{feedbackImages}
					on:resetSearch={handleReset}
					on:updateFeedbackLoop={handleUpdateFeedbackLoop}
				/>
			{:else}
				<ShowResults
					{selectedImage}
					on:resetSearch={handleReset}
					on:startFeedbackLoop={handleUpdateFeedbackLoop}
				/>
			{/if}
		{:else}
			<!-- <p class="home-subtitle">Please Select Image to Search By:</p> -->
			<ImageUploader on:imageSelected={handleImageSelected} />
		{/if}
	</div>
</div>

<style lang="scss">
	.home {
		align-self: center;
		display: flex;
		flex-direction: row;
		flex: 1;
		align-self: stretch;
		align-items: center;
		padding: 0px 10px;

		&-subtitle {
			color: var(--tertiary-text);
			font-size: 1.35em;
			font-weight: 200;
		}

		&-section {
			display: flex;
			flex-direction: column;
			flex: 1;
			gap: 10px;
		}

		@media (max-width: 875px) {
			& {
				flex-direction: column;
				justify-content: center;
			}

			&-section {
				flex: 0;
				align-items: center;
				text-align: center;
			}
		}
	}
</style>
