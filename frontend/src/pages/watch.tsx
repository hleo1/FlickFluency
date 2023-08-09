import Nav from '@/components/nav/nav';
import VideoSearchCard from '@/components/page/VideoSearchCard';
import { IVideoInfo, VideoJSON } from '@/components/page/common';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { interFont } from '@/lib/constants';
import { cn, fetcher, formatNumber, acronym } from '@/lib/utils';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import useSWR from 'swr';
import { useRef, useState, useEffect} from 'react';


export default function Watch() {
  const router = useRouter();
  const { v } = router.query;
  const videoRef = useRef<HTMLVideoElement>(null);
  const [subtitles, setSubtitles] = useState("");

  const [subtitleArray, setSubtitleArray] = useState<{
    text: string;
    start: number;
    end: number;
}[]>([]);


  const srtData = 
  `1
  00:00:01,689 --> 00:00:03,735
  [开场字幕]\n\n2
  00:00:04,021 --> 00:00:06,917
  在全职法师中...\n\n3
  00:00:07,100 --> 00:00:10,735
  我们曾经是普通的学生...\n\n4
  00:00:11,917 --> 00:00:15,021
  直到魔法门户出现\n\n5
  00:00:16,021 --> 00:00:18,917
  突然间，我们开始学习魔法。\n\n6
  00:00:19,689 --> 00:00:22,735
  [雷声轰鸣]\n\n7
  00:00:23,021 --> 00:00:26,917
  我们的命运已永远改变。\n\n8
  00:00:27,100 --> 00:00:30,735
  旅程从现在开始...`;

  function parseSrt(srtData: string) {
    
    let subtitles = srtData.split('\n\n').map((subtitleBlock) => {
      console.log(subtitleBlock);
        let lines = subtitleBlock.split('\n');
        let times = lines[1].split(' --> ').map((time) => {
            let [hours, minutes, seconds] = time.split(':');
            let [sec, ms] = seconds.split(',');
            return Number(hours) * 3600 + Number(minutes) * 60 + Number(sec) + Number(ms) / 1000;
        });

        return {
            text: lines.slice(2).join('\n'),
            start: times[0],
            end: times[1],
        };
    });

    return subtitles;
}

  useEffect(() => {
    const result: {
      text: string;
      start: number;
      end: number;
  }[] = parseSrt(srtData);
      setSubtitleArray(result);

  }, []);

  const { data, error, isLoading } = useSWR<IVideoInfo>(() => {
    if (!v) {
      router.replace('/');
      return null;
    }
    return `/api/video?id=${encodeURIComponent(
      `https://www.youtube.com/watch?v=${v}`
    )}`;
  }, fetcher);


  if (error) return <div>Failed to load</div>;
  if (!data || isLoading) return <div>Loading...</div>;

  const timeUpdate = () => {
    if (videoRef.current) {
      const currentTime = videoRef.current.currentTime;
      const currentSubtitle = subtitleArray.find(
        (subtitle) => currentTime >= subtitle.start && currentTime <= subtitle.end
      );
      setSubtitles(currentSubtitle ? currentSubtitle.text : '')
    } else {
      setSubtitles("");
    }
  }

  return (
    <>
      <Nav />
      <main className="px-6">
        <div className="flex flex-col lg:flex-row justify-between gap-4 my-4">
          <div className="flex-1">
            <video ref={videoRef} onTimeUpdate={timeUpdate} controls width = "640">
              <source src="./full-time-magister/1.mp4" type="video/mp4"  />
            </video>
            <div>{subtitles}</div>
            <div>
              <div className="py-2 flex justify-between items-center flex-col lg:flex-row">
                <div>
                  <h1 className="text-xl font-semibold">{data.video.title}</h1>
                </div>
                <div className="flex gap-2 items-center bg-secondary rounded-full p-3">
                  <div className="flex items-center gap-2 border-r dark:border-white/60 pr-4 cursor-pointer select-none">
                    <ThumbsUp className="h-5 w-5" />
                    <span>{formatNumber(data.video.ratings.likes)}</span>
                  </div>

                  <div>
                    <ThumbsDown className="h-5 w-5 cursor-pointer select-none" />
                  </div>
                </div>
              </div>
              <div className="flex gap-5 items-start">
                <Avatar>
                  <AvatarFallback>{acronym(data.video.channel.name)}</AvatarFallback>
                  <AvatarImage src={data.video.channel.icon} />
                </Avatar>
                <div>
                  <h1 className="font-semibold">{data.video.channel.name}</h1>
                  <p className="text-xs text-muted-foreground">
                    N/A subscribers
                  </p>
                </div>
              </div>
              <div className="bg-secondary my-5 p-3 rounded-lg">
                <div className="text-sm font-semibold gap-3 flex">
                  <span>{data.video.views.toLocaleString()} views</span>
                  <span>{data.video.uploadedAt}</span>
                </div>
                <div className="overflow-auto">
                  <pre
                    className={cn(interFont.className, 'break-words text-sm')}
                  >
                    {data.video.description}
                  </pre>
                </div>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <h1 className="text-sm font-semibold">Related Videos</h1>
            {data?.related.map((video) => (
              <Link href={`/watch?v=${video.id}`} key={video.id}>
                <VideoSearchCard key={video.id} video={video} small />
              </Link>
            )) || (
              <p className="text-xs text-muted-foreground">
                No data available.
              </p>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
