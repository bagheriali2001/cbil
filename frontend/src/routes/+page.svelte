<script lang="ts">
	import MainTitle from '$lib/components/MainTitle.svelte';
	import ImageUploader from '$lib/components/ImageUploader.svelte';
	import ShowResults from '$lib/components/ShowResults.svelte'; // Import the ShowResults component
	import FeedbackLoop from '$lib/components/FeedbackLoop.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';

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

	let isOpen = false;

	function toggleSidebar() {
		console.log('toggleSidebar');
		isOpen = !isOpen;
	}
</script>

<svelte:head>
	<title>CBIL Search</title>
</svelte:head>

<div class="home">
	<div class="home-section">
		<!-- Sidebar Toggle Button -->
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="menu-btn" on:click={toggleSidebar}>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				x="0px"
				y="0px"
				width="100"
				height="100"
				viewBox="0,0,256,256"
				class="menu-icon"
			>
				<g
					fill="#ffffff"
					fill-rule="nonzero"
					stroke="none"
					stroke-width="1"
					stroke-linecap="butt"
					stroke-linejoin="miter"
					stroke-miterlimit="10"
					stroke-dasharray=""
					stroke-dashoffset="0"
					font-family="none"
					font-weight="none"
					font-size="none"
					text-anchor="none"
					style="mix-blend-mode: normal"
					><g transform="scale(5.33333,5.33333)"
						><path
							d="M24,4c-1.54286,0 -3.1331,0.21506 -4.53711,0.53906c-0.62435,0.14431 -1.0881,0.66926 -1.1543,1.30664l-0.29492,2.84766c-0.14076,0.97194 -0.7179,1.87255 -1.46875,2.31055c-0.75245,0.43893 -1.89957,0.51195 -2.7168,0.13477c-0.00649,-0.0033 -0.013,-0.00656 -0.01953,-0.00977l-2.69922,-1.19922c-0.58025,-0.25794 -1.26004,-0.1226 -1.69727,0.33789c-2.05839,2.16672 -3.68342,4.87047 -4.55469,7.91992c-0.17496,0.61257 0.05607,1.26883 0.57617,1.63672l2.39844,1.69922c0.0116,0.00863 0.02332,0.0171 0.03516,0.02539c0.71997,0.47998 1.13281,1.38013 1.13281,2.35156c0,0.89815 -0.50819,1.8933 -1.17773,2.38281l-2.38867,1.69336c-0.51929,0.36761 -0.75021,1.0228 -0.57617,1.63477c0.87386,3.05852 2.5133,5.66416 4.53125,7.89453c0.43453,0.48053 1.12844,0.62782 1.7207,0.36523l2.69922,-1.20117c0.00653,-0.00256 0.01304,-0.00516 0.01953,-0.00781c0.84381,-0.38945 1.83134,-0.34172 2.75977,0.1582c0.84361,0.45425 1.35182,1.28876 1.41602,2.1875c0.00106,0.01564 0.00236,0.03127 0.00391,0.04688l0.30078,2.90039c0.06685,0.64641 0.54231,1.17628 1.17773,1.3125c1.46678,0.31431 2.97081,0.5332 4.51367,0.5332c1.54286,0 3.1331,-0.21506 4.53711,-0.53906c0.62124,-0.14311 1.08418,-0.66323 1.1543,-1.29687l0.29297,-2.65234v-0.00195c0.13966,-0.97362 0.71873,-1.8758 1.4707,-2.31445c0.75245,-0.43893 1.89957,-0.51195 2.7168,-0.13477c0.00649,0.0033 0.013,0.00656 0.01953,0.00977l2.69922,1.19922c0.58025,0.25794 1.26004,0.12261 1.69727,-0.33789c2.05839,-2.16672 3.68342,-4.87047 4.55469,-7.91992c0.17496,-0.61257 -0.05607,-1.26883 -0.57617,-1.63672l-2.39844,-1.69922c-0.0116,-0.00863 -0.02332,-0.0171 -0.03516,-0.02539c-0.71997,-0.47997 -1.13281,-1.38013 -1.13281,-2.35156c0,-0.89815 0.50819,-1.8933 1.17773,-2.38281l2.38867,-1.69336c0.51929,-0.36761 0.75021,-1.0228 0.57617,-1.63477c-0.87386,-3.05852 -2.5133,-5.66416 -4.53125,-7.89453c-0.43453,-0.48053 -1.12844,-0.62782 -1.7207,-0.36524l-2.69922,1.20117c-0.00653,0.00256 -0.01304,0.00516 -0.01953,0.00781c-0.84381,0.38946 -1.83134,0.34172 -2.75977,-0.1582c-0.84361,-0.45425 -1.35182,-1.28876 -1.41602,-2.1875c-0.00115,-0.01239 -0.00245,-0.02476 -0.00391,-0.03711l-0.29883,-3.09961c-0.06309,-0.65073 -0.54034,-1.18566 -1.17969,-1.32227c-1.46678,-0.31431 -2.97081,-0.5332 -4.51367,-0.5332zM24,7c0.91334,0 1.86873,0.17803 2.82227,0.33984l0.18164,1.86719v0.00195c0.13639,1.90054 1.22856,3.66589 2.98438,4.61133c1.67158,0.90008 3.68326,1.05274 5.43945,0.24219l1.5918,-0.70703c1.2195,1.48946 2.17983,3.11932 2.83203,4.91602l-1.41797,1.00391c-0.00523,0.00387 -0.01044,0.00778 -0.01562,0.01172c-1.52841,1.11157 -2.41797,2.9125 -2.41797,4.8125c0,1.82857 0.78872,3.72764 2.46875,4.84766l1.38477,0.98438c-0.6572,1.82537 -1.62191,3.47889 -2.82812,4.91602l-1.61523,-0.71875l0.01758,0.00977c-1.78277,-0.82282 -3.83682,-0.69545 -5.48437,0.26563c-1.64755,0.96107 -2.66692,2.6587 -2.92773,4.48438c-0.00218,0.01494 -0.00413,0.02992 -0.00586,0.04492l-0.16992,1.52734c-0.94341,0.16272 -1.91575,0.33984 -2.83984,0.33984c-0.91583,0 -1.87383,-0.17722 -2.83008,-0.33984l-0.17383,-1.66797c-0.1358,-1.90126 -1.22798,-3.66753 -2.98437,-4.61328c-1.67158,-0.90008 -3.68326,-1.05274 -5.43945,-0.24219l-1.5918,0.70703c-1.2195,-1.48946 -2.17983,-3.11932 -2.83203,-4.91602l1.41797,-1.00391c0.00523,-0.00387 0.01044,-0.00778 0.01563,-0.01172c1.52841,-1.11157 2.41797,-2.9125 2.41797,-4.8125c0,-1.82857 -0.78872,-3.72764 -2.46875,-4.84766l-1.38477,-0.98437c0.6572,-1.82537 1.62191,-3.47889 2.82812,-4.91602l1.61524,0.71875l-0.01758,-0.00977c1.78277,0.82282 3.83682,0.69545 5.48437,-0.26562c1.64755,-0.96107 2.66692,-2.6587 2.92773,-4.48437c0.00296,-0.01883 0.00557,-0.03771 0.00781,-0.05664l0.17773,-1.7168c0.94065,-0.16177 1.90914,-0.33789 2.83008,-0.33789zM24,16c-4.40051,0 -8,3.59949 -8,8c0,4.40051 3.59949,8 8,8c4.40051,0 8,-3.59949 8,-8c0,-4.40051 -3.59949,-8 -8,-8zM24,19c2.77919,0 5,2.22081 5,5c0,2.77919 -2.22081,5 -5,5c-2.77919,0 -5,-2.22081 -5,-5c0,-2.77919 2.22081,-5 5,-5z"
						/></g
					></g
				>
			</svg>
		</div>

		<Sidebar on:toggleSidebar={toggleSidebar} {isOpen} />

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

	.menu-btn {
		position: fixed;
		top: 20px;
		right: 20px;
		width: 50px;
		height: 50px;
		background: #444444;
		border-radius: 50%;
		display: flex;
		justify-content: center;
		align-items: center;
		cursor: pointer;
		box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
		transition: background 0.3s ease, transform 0.2s;
	}

	.menu-btn:hover {
		background: #333333;
		transform: scale(1.1);
	}

	.menu-icon {
		width: 30px;
		height: 30px;
		fill: white;
	}
</style>
