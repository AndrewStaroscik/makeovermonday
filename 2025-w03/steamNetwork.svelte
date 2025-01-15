<script>
  /** 
   * This is a svelte component, with access to the data on a server, 
   * This component should function within any svelte environment
   * 
  */
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let data = null; 
  let vizVar, vizWidth, svg, g;

  const nodeColor = '#0b81a2';
  const toColor = '#e25759';
  const byColor = '#36b700';
  const bothColor = '#7e4794';
  const baseGrey = '#d9d9d9';

  const maxW = 920;

  let totalWidth = 600;
  let totalHeight = 500;
  let margin = {top:30, bottom: 65, left: 105, right: 30};
  let height = totalHeight - margin.top - margin.bottom;
  let width = totalWidth - margin.left - margin.right;
  let labelSize, bodyForceVar, linkDistance, forceRad, sizeAdj, edgeAdj, nodeSizeMultiplier;

  const adjVar = (maxV, s, maxS) => {
    let tempVar = s >= maxS ? maxV : maxV * s / maxS;
    return tempVar;
  }

  const resize = () => {

    if (!data) return;

    vizWidth = document.getElementById('viscontainer').offsetWidth;
    console.log(vizWidth)
    totalWidth = adjVar(920, vizWidth, maxW);
    totalHeight = adjVar(600, vizWidth, maxW);
    margin.top = adjVar(10, vizWidth, maxW);
    margin.bottom = adjVar(10, vizWidth, maxW);
    margin.left = adjVar(40, vizWidth, maxW);
    margin.right = adjVar(80, vizWidth, maxW);
    height = totalHeight - margin.top - margin.bottom;
    width = totalWidth - margin.left - margin.right;

    labelSize = adjVar(17, vizWidth, maxW);
    bodyForceVar = adjVar(-8, vizWidth, maxW);
    linkDistance = adjVar(40, vizWidth, maxW);
    forceRad = adjVar(15, vizWidth, maxW);
    sizeAdj = adjVar(1, vizWidth, maxW);
    edgeAdj = adjVar(50, vizWidth, maxW);
    nodeSizeMultiplier = adjVar(1/3e4, vizWidth, maxW);

    makeChart();

  }
  
  const makeChart = () => {
    if (!data) return;

    const sizeData = [10, 20, 30]

    const linkDescs = [
      {col: toColor, desc: 'Similar To'},
      {col: byColor, desc: 'Considered Similar By'},
      {col: bothColor, desc: 'Both'},
    ]

    data.nodes.forEach(function(el) {
      el['nodeSize'] = parseInt(el['popularity'].replace(/,/g, ''), 10)*nodeSizeMultiplier;
    })
    
    const dragstarted = (event, d) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    const dragged = (event, d) => {
      d.fx = event.x;
      d.fy = event.y;
    }
    const dragended = (event, d) => {
      if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    const handleMouseOver = (event, d) => {
  
      link
        .style('stroke', l => {
          const isSource = l.source.game === d.game;
          const isTarget = l.target.game === d.game;

          if (l.twoWay === 1 && (isSource || isTarget)) {
            return bothColor;
          } else if (isSource) {
            return toColor; 
          } else if (isTarget) {
            return byColor; 
          } else {
            return baseGrey;
          }
        })
        .attr('stroke-width', l => {
          const isConnected = l.source.game === d.game || l.target.game === d.game;
          return isConnected ? 3 : 1;
        });

        // hack to find links so that the names can be shown
        const connectedNodes = new Set();
        data.links.forEach(link => {
          if (link.source.game === d.game) {
            connectedNodes.add(link.target.game);
          } else if (link.target.game === d.game) {
            connectedNodes.add(link.source.game);
          }
        });

        labels
          .style("opacity", l => (l.game === d.game || connectedNodes.has(l.game) ? 1 : 0));
    } // end handleMouseOver
    const handleMouseOut = (event, d) => {
    
      link
        .style('stroke', baseGrey)
        .attr('stroke-width', 1);

      labels.style('opacity', 0);     
    } // end handleMouseOut

    vizVar = d3.select('#viscontainer')
    vizVar.html(null)
    console.log(`total width: ${totalWidth}`)
    svg = d3.select('#viscontainer').append('svg')
      .attr('width', totalWidth)
      .attr('height', totalHeight)

    let chartG = svg.append('g')
      .attr('transform', `translate(${[margin.left, margin.top]})`);
    
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.game).distance(linkDistance))
      .force('charge', d3.forceManyBody().strength(bodyForceVar))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.nodeSize + forceRad));
    
    const link = chartG.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(data.links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .style('stroke', '#d9d9d9');

    const node = chartG.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(data.nodes)
      .enter()
      .append('circle')
      .attr('class', 'node')
      .attr('r', d => d.nodeSize < 3 ? 3 : d.nodeSize)
      .attr('fill', nodeColor)
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('mouseover', handleMouseOver)
      .on('mouseout', handleMouseOut);  
        
    const labels = chartG.append('g')
      .attr('class', 'labels')
      .selectAll('text')
      .data(data.nodes)
      .enter()
      .append('text')
      .attr('x', 8)
      .attr('y', 3)
      .attr('opacity', 0)
      .attr('font-size', labelSize)
      .style('fill', d3.color(nodeColor).darker(3))
      .style('stroke-width', 0.5)
      .style('pointer-events', 'none')
      .text(d => d.game);

    simulation.on('tick', () => {
 
      node
        .attr('cx', d => {
          d.x = Math.max(edgeAdj, Math.min(width - edgeAdj, d.x)); 
          return d.x;
        })
        .attr('cy', d => {
          d.y = Math.max(edgeAdj, Math.min(height - edgeAdj, d.y)); 
          return d.y;
        });

      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      labels
        .attr("x", d => d.x + 8)
        .attr("y", d => d.y + 3);

    }); // end simulation.on('tick')


    chartG.selectAll('.sizecircs')
      .data(sizeData)
      .enter()
      .append('circle')
      .attr('class', '.sizecircs')
      .attr('cx', width - 50)
      .attr('cy', d => {
        return 100 - (d) - (sizeData[sizeData.length-1]/2)
      })
      .attr('r', d => d)
      .style('stroke', nodeColor)
      .style('fill', 'none')
      .style('stroke-width', 2);

    chartG.append('text')
      .attr('x', width-50)
      .attr('y', 100)
      .attr('text-anchor', 'middle')
      .attr('fill', nodeColor)
      .text('Popularity')

    const linkDescEl = chartG.selectAll('.linkdesc')
      .data(linkDescs)
      .enter()
      .append('g')
      .attr('class', 'linkdesc')
      .attr('transform', (d, i) => {
        return `translate(${20}, ${40 + 30*i})`
      })

    linkDescEl.append('line')
      .attr('x1', 0)  
      .attr('y1', 0)  
      .attr('x2', 60)  
      .attr('y2', 0)
      .style('stroke', d => d.col)
      .style('stroke-width', 3)  

    // adding directional arrows to the link lines would be an improvement

    linkDescEl.append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', 10)
      .style('fill', nodeColor)

    linkDescEl.append('text')
      .attr('x', 65)
      .attr('y', 0)
      .attr('dominant-baseline', 'middle')
      .attr('font-size', labelSize)
      .text(d => d.desc)

    chartG.append('text')
      .attr('x', width - 100)
      .attr('y', height - 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', labelSize+2)
      .style('fill', '#a9a9a9')
      .text('Andrew Staroscik')

      chartG.append('text')
      .attr('x', width - 100)
      .attr('y', height - 15)
      .attr('text-anchor', 'middle')
      .attr('font-size', labelSize-1)
      .style('fill', '#a9a9a9')
      .text('#MakeoverMonday')
  } // end makeChart

  $: resize(data)

  onMount(async () => {

    data = await d3.json('../data/gamesAsNodes.json');

    for (let i = 0; i < data.links.length; i += 1) {
      let tmpSource = data.links[i].source;
      let tmpTarget = data.links[i].target;

      // find and label the reciprical links (so they can be purple on hover)
      let tmpTwoWay = 0;    
      for (let j = 0; j < data.links.length; j += 1) {
        if (data.links[j].source === tmpTarget && data.links[j].target === tmpSource) {
          tmpTwoWay = 1;
          break;
        }
      }
      data.links[i].twoWay = tmpTwoWay
    
    }
    
    // add listner for resizing vis
    window.addEventListener('resize', resize);

    return () => {
      window.removeEventListener('resize', resize);
    };
  })

</script>



<div style='font-size: 1.3em'>Mapping Similarities in Steam Games by Genre Overlap</div>
<div id="viscontainer"></div>
<div class='bottomlabel'>Source: <a href='https://data.world/makeovermonday/2025w3-steam-top-100-played-games'>Steam</a></div>

<style>

  body {
    margin: 0;
  }

  #viscontainer {
    width: 100vw;
  }

  .bottomlabel {
    text-align: left;
    margin: 0px 100px;
  }

</style>