<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	let imageFile: File | null = null;
	let previewSrc: string | null = null;
	let dragActive: boolean = false;

	const dispatch = createEventDispatcher();

	function handleFileSelection(event: Event): void {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file && file.type.startsWith('image/')) {
			setPreview(file);
		} else {
			alert('Please select a valid image file.');
		}
	}

	function handleDrop(event: DragEvent): void {
		event.preventDefault();
		dragActive = false;

		const file = event.dataTransfer?.files[0];
		if (file) {
			if (file.type.startsWith('image/')) {
				setPreview(file);
			} else {
				alert('Only image files are allowed.');
			}
		}
	}

	function setPreview(file: File): void {
		imageFile = file;
		previewSrc = URL.createObjectURL(file);
	}

	function resetSelection(): void {
		imageFile = null;
		previewSrc = null;
	}

	function handleDragOver(event: DragEvent): void {
		event.preventDefault();
		dragActive = true;
	}

	function handleDragLeave(event: DragEvent): void {
		event.preventDefault();
		dragActive = false;
	}

	function handleKeyPress(event: KeyboardEvent): void {
		if (event.key === 'Enter' || event.key === ' ') {
			document.getElementById('fileInput')?.click();
			event.preventDefault();
		}
	}

	function confirmSelection(): void {
		if (imageFile) {
			dispatch('imageSelected', { file: imageFile });
		}
	}
</script>

<div
	class="uploader {dragActive ? 'drag-active' : ''}"
	role="button"
	tabindex="0"
	aria-label="Upload image"
	on:dragover={handleDragOver}
	on:dragleave={handleDragLeave}
	on:drop={handleDrop}
	on:click={() => (!imageFile ? document.getElementById('fileInput')?.click() : {})}
	on:keydown={handleKeyPress}
>
	<input
		id="fileInput"
		type="file"
		accept="image/*"
		class="file-input"
		on:change={handleFileSelection}
	/>
	{#if previewSrc}
		<img src={previewSrc} alt="Preview" />
		<div class="button-group">
			<button class="confirm-btn" on:click={confirmSelection}> Confirm Selection </button>
			<button class="reset-btn" on:click={resetSelection}> Select Again </button>
		</div>
	{:else}
		<p>Drag & drop an image here, or click to select one</p>
	{/if}
</div>

<style>
	.uploader {
		border: 2px dashed var(--light-7);
		border-radius: 8px;
		padding: 20px;
		text-align: center;
		position: relative;
		cursor: pointer;
		background-color: var(--dark-3);
		transition: background-color 0.3s ease;
		width: 90%;
		height: 50vh;
		margin: 5%;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}

	.uploader.drag-active {
		border-color: var(--active-primary);
	}

	.uploader img {
		height: 85%;
		margin-top: 10px;
		border-radius: 8px;
	}

	.file-input {
		display: none;
	}

	.uploader p {
		font-size: 16px;
		color: var(--light-3);
	}

	.button-group {
		margin-top: 20px;
		display: flex;
		gap: 10px;
	}

	.confirm-btn,
	.reset-btn {
		padding: 10px 20px;
		font-size: 16px;
		border-radius: 5px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		border: none;
		color: var(--light-0);
	}

	.confirm-btn {
		background-color: var(--update-primary);
	}

	.confirm-btn:hover {
		background-color: var(--update-primary-hover);
	}

	.reset-btn {
		background-color: var(--reset-primary);
	}

	.reset-btn:hover {
		background-color: var(--reset-primary-hover);
	}
</style>
